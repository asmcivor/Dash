from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My Dashboard"
    debug: bool = False
    database_url: str = "sqlite:///./dashboard.db"

    # Add API keys, secrets, etc.
    # secret_key: str = "change-me"

    class Config:
        env_file = ".env"


settings = Settings()
