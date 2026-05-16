import sys
import os
import time
from src.core.auth import get_credentials, get_authorized_session
from src.core.config import get_settings
from src.connector.drive_client import DriveConnector

def setup_drive_webhook(webhook_url: str, token: str | None, expiration_hours: int = 168) -> None:
    settings = get_settings()

    folder_id = settings.DRIVER_FOLDER_ID
    if not folder_id:
        print("Error: DRIVE_FOLDER_ID is not configured")
        sys.exit(1)

    secret_token = token or settings.WEBHOOK_SECRET_TOKEN or None
    current_time_ms = int(time.time() * 1000)
    expiration_ms = current_time_ms + (expiration_hours * 60 * 60 * 1000)

    credentials, _ = get_credentials()
    session = get_authorized_session(credentials)
    connector = DriveConnector(session)

    print(f"Registering watch channel for folder: {folder_id}")
    print(f"  Webhook URL  : {webhook_url}")
    print(f"  Expiration   : {expiration_hours}h ({expiration_ms} ms)")
    print(f"  Token set    : {'yes' if secret_token else 'no (not recommended)'}")

    try:
        info = connector.watch_folder(
            folder_id=folder_id,
            webhook_url=webhook_url,
            token=secret_token,
            expiration_ms=expiration_ms,
        )

        print("\nWebhook registered successfully!")
        resp = info["response"]
        print(f"  Channel ID   : {resp.get('id')}")
        print(f"  Resource ID  : {resp.get('resourceId')}")
        print(f"  Expiration   : {resp.get('expiration')} (Epoch MS)")

    except Exception as e:
        print(f"Error registering webhook: {e}")
        sys.exit(1)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("WEBHOOK_URL")

    if not url:
        print("Error: Webhook URL is requires as an argument or WEBHOOK_URL env var")
    else:
        setup_drive_webhook(
            webhook_url=url,
            token=os.getenv("WEBHOOK_SECRET_TOKEN"),
            expiration_hours=1,
        )
