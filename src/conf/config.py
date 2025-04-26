from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DB_URL: str = Field(..., env="DB_URL")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(..., env="JWT_ALGORITHM")
    JWT_EXPIRATION_SECONDS: int = Field(..., env="JWT_EXPIRATION_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
