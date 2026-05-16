from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- GCP PROJECT ---
    PROJECT_ID: str = ""

    # --- Pub/Sub ---
    PUB_SUB_TOPIC: str = ""
    PUB_SUB_SUBSCRIPTION: str = ""   

    # --- BigQuery ---
    BQ_DATASET: str = ""
    BQ_TABLE: str = ""
    BQ_LOCATION: str = "US"

    # --- Google Drive ---
    DRIVER_FOLDER_ID: str = ""

    # --- Security ---
    WEBHOOK_SECRET_TOKEN: str = ""

    # --- Salesforce ---
    SF_USERNAME: str = ""
    SF_PASSWORD: str = ""
    SF_SECURITY_TOKEN: str = ""

    # --- Vertex AI / Gemini ---
    VERTEX_AI_LOCATION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()