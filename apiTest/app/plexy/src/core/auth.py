from google.auth import default
from google.auth.transport.requests import AuthorizedSession
from google.cloud import bigquery
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Scopes required by the connector
_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/pubsub",
]


def get_credentials():
    """Returns authorized credentials for the required scopes."""
    credentials, project = default(scopes=_SCOPES)
    return credentials, project


def get_authorized_session(credentials) -> AuthorizedSession:
    """
    Returns a requests-based AuthorizedSession with automatic retry.
    """
    session = AuthorizedSession(credentials)
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_bigquery_client(credentials, project):
    """Returns an authorized BigQuery client."""
    return bigquery.Client(credentials=credentials, project=project)
