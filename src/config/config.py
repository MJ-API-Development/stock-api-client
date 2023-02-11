import functools
from pydantic import BaseSettings, Field


class EmailSettings(BaseSettings):
    EMAIL_HOST: str = Field(..., env="EMAIL_HOST")
    EMAIL_PORT: int = Field(..., env="EMAIL_PORT")
    EMAIL_USE_TLS: bool = Field(default=False)
    EMAIL_USE_SSL: bool = Field(default=True)
    EMAIL_HOST_USER: str = Field(..., env="EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD: str = Field(..., env="EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL: str = Field(..., env="DEFAULT_FROM_EMAIL")

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class CelerySettings(BaseSettings):
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_BACKEND: str = Field(..., env="CELERY_BACKEND")

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class Settings(BaseSettings):
    EMAIL_SETTINGS: EmailSettings = EmailSettings()
    CELERY_SETTINGS = CelerySettings()

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


@functools.lru_cache
def config_instance():
    return Settings()
