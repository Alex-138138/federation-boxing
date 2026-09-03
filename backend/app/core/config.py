from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str = "postgresql+psycopg://boxing:boxing@db:5432/boxing"
    jwt_secret: str = "change-me"
    access_token_minutes: int = 60
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:admin@example.org"
    cors_origins: str = "http://localhost"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
