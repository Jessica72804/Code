from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Pharmacy Inventory API")
    debug: bool = Field(default=True)

    # Default to local SQLite database in project root
    database_url: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./pharmacy.db"))


settings = Settings()
