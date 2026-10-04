import os
from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AegisGov AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8080
    HOST: str = "0.0.0.0"

    # Google Cloud & Agentic AI Configuration
    GCP_MODE: str = "local"  # "local" (emulator) or "cloud" (Vertex AI / BigQuery / PubSub)
    GEMINI_API_KEY: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = "aegisgov-ai-2026"
    GCP_LOCATION: str = "asia-southeast1"  # Singapore
    GEMINI_MODEL_FLASH: str = "gemini-2.0-flash"
    GEMINI_MODEL_PRO: str = "gemini-1.5-pro"
    PUBSUB_TOPIC_TRANSACTIONS: str = "japac-rail-transactions"
    BIGQUERY_DATASET: str = "aegisgov_lakehouse"

    # JAPAC Currency Defaults & Financial Thresholds
    BASE_CURRENCY: str = "SGD"
    HIGH_VALUE_THRESHOLD_SGD: float = 10000.00
    HIGH_VALUE_THRESHOLD_INR: float = 500000.00

    # TBAC Default TTL in seconds
    DEFAULT_TBAC_TTL_SECONDS: int = 1800  # 30 mins

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @model_validator(mode="after")
    def auto_harden_production_flags(self) -> 'Settings':
        # Security hardening: Prevent traceback disclosure in production
        if self.ENVIRONMENT.lower() == "production":
            self.DEBUG = False
        return self

settings = Settings()
