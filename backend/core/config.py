from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME:     str = "kca_database"
    DB_USER:     str = "kca_admin"
    DB_PASSWORD: str = "secretpassword"
    DB_HOST:     str = "db"
    DB_PORT:     int = 5432

    MODEL_CLASSIFIER:       str = "models/kca_classifier_v2.pkl"
    MODEL_PIPELINE_ARTIFACTS: str = "models/pipeline_artifacts.pkl"
    MODEL_SCALER:           str = "models/structural_scaler.pkl"
    SENTENCE_MODEL:   str = "all-MiniLM-L6-v2"

    CORS_ORIGINS: list[str] = ["*"]

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"
    MODEL_RETRAINED: str = "models/kca_classifier_retrained.cbm"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()