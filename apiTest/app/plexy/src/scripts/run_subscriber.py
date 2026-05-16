import argparse
import logging
import sys

from src.core.auth import get_authorized_session, get_bigquery_client, get_credentials
from src.core.config import get_settings
from src.services.docs_processor import DocsProcessor
from src.services.pubsub_subscriber import PubSubSubscriber

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run the Pub/Sub subscriber worker.")
    parser.parse_args()

    settings = get_settings()

    # Authenticate
    logger.info("Authenticating via Application Default Credentials (ADC)...")
    try:
        credentials, project = get_credentials()
    except Exception as e:
        logger.error(f"Failed to get Google Cloud credentials: {e}")
        sys.exit(1)

    # Build clients
    logger.info("Initializing Google API clients...")
    session   = get_authorized_session(credentials)
    bq_client = get_bigquery_client(credentials, project)

    # Inject dependencies
    processor = DocsProcessor(
        session=session,
        bq_client=bq_client,
        settings=settings,
    )
    
    subscriber = PubSubSubscriber(processor=processor, settings=settings)

    # Start consuming messages
    try:
        subscriber.run()
    except KeyboardInterrupt:
        logger.info("Subscriber stopped manually.")
    except Exception as e:
        logger.exception(f"Subscriber encountered an unhandled error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
