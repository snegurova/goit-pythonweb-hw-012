from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    db_url: str = Field(..., env="DB_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = Settings()