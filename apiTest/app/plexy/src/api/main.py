"""
FastAPI application — Drive webhook receiver + Pub/Sub push endpoint.

Two modes of operation:
  1. Local dev  — Drive → /webhook/drive → Pub/Sub topic → run_subscriber (pull)
  2. Cloud Run  — Drive → /webhook/drive → Pub/Sub topic
                                             └─ push subscription → /webhook/pubsub
                                                                      └─ DocsProcessor

The /webhook/pubsub endpoint lets Cloud Run scale to zero: Pub/Sub wakes the
service on demand, so no long-running pull worker is needed in production.
"""

import base64
import json
import logging
import re
import time
from contextlib import asynccontextmanager
from threading import Lock
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from google.cloud import pubsub_v1

from src.core.auth import get_authorized_session, get_bigquery_client, get_credentials
from src.core.config import get_settings
from src.services.docs_processor import DocsProcessor

logger = logging.getLogger(__name__)
settings = get_settings()

_DEDUP_WINDOW_SECS = 30.0
_seen_resources: dict[str, float] = {}
_seen_lock = Lock()

_PUBSUB_DEDUP_WINDOW = 60.0
_seen_pubsub: dict[str, float] = {}
_seen_pubsub_lock = Lock()


def _should_publish(resource_id: str) -> bool:
    """Returns True only for the first notification of a resource_id within the dedup window."""
    now = time.monotonic()
    with _seen_lock:
        # Evict stale entries to prevent unbounded memory growth
        stale = [k for k, ts in _seen_resources.items() if now - ts >= _DEDUP_WINDOW_SECS]
        for k in stale:
            del _seen_resources[k]

        if resource_id in _seen_resources:
            return False
        _seen_resources[resource_id] = now
        return True


def _should_process_pubsub(message_id: str) -> bool:
    """Dedup Pub/Sub push deliveries by messageId."""
    now = time.monotonic()
    with _seen_pubsub_lock:
        stale = [k for k, ts in _seen_pubsub.items() if now - ts >= _PUBSUB_DEDUP_WINDOW]
        for k in stale:
            del _seen_pubsub[k]
        if message_id in _seen_pubsub:
            return False
        _seen_pubsub[message_id] = now
        return True

_credentials   = None
_bq_client     = None
_drive_session = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _credentials, _bq_client, _drive_session
    _credentials, project = get_credentials()
    _bq_client     = get_bigquery_client(_credentials, project)
    _drive_session = get_authorized_session(_credentials)
    logger.info("Shared clients initialized and ready.")
    yield


def _build_processor() -> DocsProcessor:
    """Builds a DocsProcessor using the shared AuthorizedSession."""
    return DocsProcessor(
        session=_drive_session,
        bq_client=_bq_client,
        settings=settings,
    )


app = FastAPI(
    title="Plexy Flow - Meeting Summary",
    description=(
        "Receives Google Drive push notifications, processes Meet transcripts "
        "stores structured metadata in BigQuery."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

publisher  = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(settings.PROJECT_ID, settings.PUB_SUB_TOPIC)


@app.get("/")
def read_root():
    return {"message": "Plexy Flow - Meeting Summary is running"}


@app.post("/api/v1/webhook/drive")
async def drive_webhook(
    request: Request,
    x_goog_resource_state: str = Header(None),
    x_goog_channel_id: str = Header(None),
    x_goog_channel_token: str = Header(None),
    x_goog_resource_id: str = Header(None),
    x_goog_resource_uri: str = Header(None),
):
    """
    Receives Drive push notifications and publishes them to Pub/Sub.
    Works in both local (pull subscriber) and Cloud Run (push subscription) modes.
    """
    if x_goog_resource_state == "sync":
        return {"status": "synced"}

    if settings.WEBHOOK_SECRET_TOKEN and x_goog_channel_token != settings.WEBHOOK_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid channel token")

    file_id = None
    if x_goog_resource_uri:
        match = re.search(r"/files/([^/?]+)", x_goog_resource_uri)
        if match:
            file_id = match.group(1)

    # Folder-watch notifications don't carry a file ID in the URI.
    # Fall back to the configured folder so DocsProcessor can list its children.
    if not file_id:
        file_id = settings.DRIVER_FOLDER_ID
        logger.info(
            "No file ID in resource URI — treating as folder change (folder=%s, resource_id=%s)",
            file_id, x_goog_resource_id,
        )

    # Suppress duplicate notifications for the same resource within the dedup window.
    if not _should_publish(file_id):
        logger.debug("Suppressing duplicate Drive notification for resource %s", file_id)
        return {"status": "deduplicated"}

    message = {
        "state": x_goog_resource_state,
        "resource_id": file_id,
        "channel_id": x_goog_channel_id,
    }

    future = publisher.publish(TOPIC_PATH, json.dumps(message).encode("utf-8"))
    await run_in_threadpool(future.result)

    return {"status": "accepted"}


@app.post("/api/v1/webhook/pubsub")
async def pubsub_push_webhook(request: Request):
    """
    Pub/Sub push subscription endpoint (Cloud Run production mode).

    Pub/Sub delivers messages as:
      { "message": { "data": "<base64>", "messageId": "...", ... }, "subscription": "..." }

    Returns 200 on success (tells Pub/Sub to ack).
    Returns 500 on failure (tells Pub/Sub to redeliver — acts as a nack).
    """
    if _drive_session is None:
        raise HTTPException(status_code=503, detail="Processor not ready")

    body = await request.json()
    message = body.get("message", {})

    message_id = message.get("messageId", "")
    if message_id and not _should_process_pubsub(message_id):
        logger.debug("Suppressing duplicate Pub/Sub message %s", message_id)
        return {"status": "deduplicated"}

    raw_data = message.get("data", "")
    if not raw_data:
        return {"status": "ignored"}

    try:
        payload_bytes = base64.b64decode(raw_data)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as exc:
        logger.error("Failed to decode Pub/Sub push message: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid message encoding")

    try:
        processor = _build_processor()
        await run_in_threadpool(processor.process_notification, payload)
    except Exception as exc:
        logger.exception("Error processing Pub/Sub push message: %s", exc)
        raise HTTPException(status_code=500, detail="Processing failed — will retry")

    return {"status": "processed"}


@app.post("/api/v1/renew-webhook")
async def renew_webhook(request: Request):
    """
    Renews the Google Drive webhook subscription.
    """
    if _credentials is None:
        raise HTTPException(status_code=503, detail="Processor not ready")

    try:
        body = await request.json()
        webhook_url = body.get("webhook_url")
    except Exception:
        webhook_url = None

    if not webhook_url:
        raise HTTPException(status_code=400, detail="Missing 'webhook_url' in JSON body")


    expiration_hours = 168
    current_time_ms = int(time.time() * 1000)
    expiration_ms = current_time_ms + (expiration_hours * 60 * 60 * 1000)

    try:
        processor = _build_processor()
        info = await run_in_threadpool(
            processor._drive.watch_folder,
            folder_id=settings.DRIVER_FOLDER_ID,
            webhook_url=webhook_url,
            token=settings.WEBHOOK_SECRET_TOKEN,
            expiration_ms=expiration_ms,
        )
        logger.info("Successfully renewed webhook for 7 days.")
        return {
            "status": "success",
            "channel_id": info["response"].get("id"),
            "expiration_epoch_ms": info["response"].get("expiration"),
        }
    except Exception as exc:
        logger.exception("Failed to renew webhook: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
