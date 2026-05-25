"""
Application settings loaded from the .env file.
pydantic-settings validates every value at startup.
If a required variable is missing, the app fails immediately with a clear error.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    async_database_url: str 
    sync_database_url: str

    # OpenAI
    openai_api_key: str
    embedding_model: str
    embedding_dimensions: int


    

# model_config = SettingsConfigDict(env_file=".env")