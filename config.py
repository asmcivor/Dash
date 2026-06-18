from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Alan McIvor"
    debug: bool = False
    database_url: str = "sqlite:///./dashboard.db"
    geocoding_api_key: str
    open_meteo_api_key: str = ""  # Open-Meteo does not require an API key

settings = Settings()