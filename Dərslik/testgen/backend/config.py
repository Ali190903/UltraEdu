from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://testgen:testgen@db:5432/testgen"
    database_url_sync: str = "postgresql://testgen:testgen@db:5432/testgen"
    qdrant_url: str = "http://qdrant:6333"
    gemini_api_key: str = ""
    # Məhsulda hər proses/worker eyni dəyəri oxumalıdır; boş qalsa main.py RuntimeError atır.
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    cookie_secure: bool = False  # Set True in production (.env: COOKIE_SECURE=true)
    google_client_id: str = ""
    google_client_secret: str = ""
    similarity_threshold: float = 0.88
    max_generation_attempts: int = 3

    # Data Pipeline (local paths, not used in Docker)
    textbook_dir: str = ""
    dim_test_dir: str = ""


settings = Settings()