from pydantic_settings import BaseSettings
from pydantic import Field, EmailStr

class Settings(BaseSettings):
    DB_URL: str = Field(..., env="DB_URL")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(..., env="JWT_ALGORITHM")
    JWT_EXPIRATION_SECONDS: int = Field(..., env="JWT_EXPIRATION_SECONDS")

    MAIL_USERNAME: EmailStr = Field(..., env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")
    MAIL_FROM: EmailStr = Field(..., env="MAIL_FROM")
    MAIL_PORT: int = Field(..., env="MAIL_PORT")
    MAIL_SERVER: str = Field(..., env="MAIL_SERVER")
    MAIL_FROM_NAME: str = "Inna"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str = Field(..., env="CLD_NAME")
    CLD_API_KEY: int = Field(..., env="CLD_API_KEY")
    CLD_API_SECRET: str = Field(..., env="CLD_API_SECRET")

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
