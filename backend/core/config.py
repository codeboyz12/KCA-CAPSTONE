from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME:     str = "kca_database"
    DB_USER:     str = "kca_admin"
    DB_PASSWORD: str = "secretpassword"
    DB_HOST:     str = "db"
    DB_PORT:     int = 5432

    MODEL_CLASSIFIER: str = "models/kca_classifier.pkl"
    MODEL_REGRESSOR:  str = "models/kca_regressor.pkl"
    MODEL_ENCODER:    str = "models/category_encoder.pkl"
    MODEL_SCALER:     str = "models/structural_scaler.pkl"
    SENTENCE_MODEL:   str = "all-MiniLM-L6-v2"

    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()