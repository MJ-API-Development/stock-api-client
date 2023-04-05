import functools
from pydantic import BaseSettings, Field
import socket


def get_server_name():
    return "eod-stock-api.local:8081" if socket.gethostname() == "DESKTOP-T9V7F59" else "eod-stock-api.site"


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
    CELERY_RESULT_ENGINE_OPTIONS: dict[str, bool] = {"echo": True}
    CELERY_RESULT_BACKEND: str = "database"
    BROKER_TRANSPORT: str = Field(default="sqlakombu.transport.Transport")
    BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_DBURI: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_ACCEPT_CONTENT: list[str] = Field(default=['application/json'])
    CELERY_TASK_SERIALIZER: str = Field(default='json')
    CELERY_RESULT_SERIALIZER: str = Field(default='json')

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class DatabaseSettings(BaseSettings):
    SQL_DB_URL: str = Field(..., env='SQL_DB_URL')
    TOTAL_CONNECTIONS: int = Field(default=1000)

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class Logging(BaseSettings):
    filename: str = Field(default="eod_stock_api.logs")

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class GatewaySettings(BaseSettings):
    LOGIN_URL: str = Field(..., env="GATEWAY_LOGIN_URL")
    CREATE_USER_URL: str = Field(..., env="GATEWAY_CREATE_USER_URL")
    AUTHORIZE_URL: str = Field(..., env="GATEWAY_AUTHORIZE_USER_URL")
    BASE_URL: str = Field(..., env="GATEWAY_URL")
    LOCAL_BASE_URL: str = Field(..., env="LOCAL_GATEWAY_URL")

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class GithubSettings(BaseSettings):
    GITHUB_BLOG_TOKEN: str = Field(..., env="GIHUB_BLOG_TOKEN")
    BLOG_REPO: str = Field(..., env="BLOG_REPO")

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class Settings(BaseSettings):
    EMAIL_SETTINGS: EmailSettings = EmailSettings()
    CELERY_SETTINGS = CelerySettings()
    SECRET_KEY: str = Field(..., env="SECRET_TOKEN")
    DATABASE_SETTINGS: DatabaseSettings = DatabaseSettings()
    DEVELOPMENT_SERVER_NAME: str = Field(default="DESKTOP-T9V7F59")
    LOGGING: Logging = Logging()
    DEBUG: bool = True
    GATEWAY_SETTINGS: GatewaySettings = GatewaySettings()
    SERVER_NAME: str = Field(default_factory=get_server_name)
    APPLICATION_ROOT: str = Field(default="/")
    PREFERRED_URL_SCHEME: str = Field(default="https://")
    GITHUB_SETTINGS: GithubSettings = GithubSettings()

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


@functools.lru_cache
def config_instance():
    return Settings()
