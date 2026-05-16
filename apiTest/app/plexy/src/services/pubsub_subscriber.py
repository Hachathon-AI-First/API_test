"""
Pub/Sub subscriber for Google Drive notifications.

Uses a simple synchronous pull loop (single-threaded) so the
google-api-python-client can be used without any thread-safety hacks.
"""

import json
import logging
import time

from google.cloud import pubsub_v1
from google.api_core.exceptions import DeadlineExceeded

from src.core.config import Settings
from src.services.docs_processor import DocsProcessor

logger = logging.getLogger(__name__)

_PULL_MAX_MESSAGES  = 1
_PULL_TIMEOUT_SECS  = 10.0
_IDLE_SLEEP_SECS    = 2.0
_ACK_EXTENSION_SECS = 60


class PubSubSubscriber:
    """
    Synchronous pull-based subscriber.

    Pulls one message at a time, processes it, then ack/nacks before
    fetching the next one. This avoids any multi-threading and keeps
    the Google API clients fully single-threaded.
    """

    def __init__(self, processor: DocsProcessor, settings: Settings):
        self._processor = processor
        self._settings = settings
        self._client = pubsub_v1.SubscriberClient()
        self._subscription = self._client.subscription_path(
            settings.PROJECT_ID, settings.PUB_SUB_SUBSCRIPTION
        )

        self._processed_ids: set[str] = set()

    def run(self) -> None:
        """Blocking loop: pull → extend deadline → process → ack/nack → repeat."""
        logger.info("Starting synchronous pull subscriber on %s", self._subscription)

        with self._client:
            while True:
                try:
                    response = self._client.pull(
                        request={
                            "subscription": self._subscription,
                            "max_messages": _PULL_MAX_MESSAGES,
                        },
                        timeout=_PULL_TIMEOUT_SECS,
                    )
                except DeadlineExceeded:
                    # no messages available within timeout
                    time.sleep(_IDLE_SLEEP_SECS)
                    continue
                except Exception:
                    logger.exception("Pull request failed. Retrying in %ss.", _IDLE_SLEEP_SECS)
                    time.sleep(_IDLE_SLEEP_SECS)
                    continue

                if not response.received_messages:
                    time.sleep(_IDLE_SLEEP_SECS)
                    continue

                for received_msg in response.received_messages:
                    msg = received_msg.message
                    ack_id = received_msg.ack_id
                    logger.info("Received message ID: %s", msg.message_id)

                    # Extend ack deadline before processing
                    try:
                        self._client.modify_ack_deadline(
                            request={
                                "subscription": self._subscription,
                                "ack_ids": [ack_id],
                                "ack_deadline_seconds": _ACK_EXTENSION_SECS,
                            }
                        )
                    except Exception:
                        logger.warning(
                            "Could not extend ack deadline for %s — redelivery possible.",
                            msg.message_id,
                        )

                    if msg.message_id in self._processed_ids:
                        logger.info(
                            "Skipping duplicate message %s (already processed this session).",
                            msg.message_id,
                        )
                        self._client.acknowledge(
                            request={
                                "subscription": self._subscription,
                                "ack_ids": [ack_id],
                            }
                        )
                        continue

                    try:
                        payload = json.loads(msg.data.decode("utf-8"))
                        self._processor.process_notification(payload)

                        self._client.acknowledge(
                            request={
                                "subscription": self._subscription,
                                "ack_ids": [ack_id],
                            }
                        )
                        self._processed_ids.add(msg.message_id)
                        logger.info("Acked message %s", msg.message_id)

                    except Exception:
                        logger.exception(
                            "Error processing message %s. Will be redelivered.", msg.message_id
                        )
