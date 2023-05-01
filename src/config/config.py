import functools
from pydantic import BaseSettings, Field
import socket


def is_development() -> bool:
    """returns true if running in development mode"""
    return socket.gethostname().casefold() == config_instance().DEVELOPMENT_SERVER_NAME.casefold()


def get_server_name():
    """will return the hostname of the server to use"""
    return "eod-stock-api.local:8081" if is_development else "eod-stock-api.site"


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
    GITHUB_BLOG_TOKEN: str = Field(..., env="GITHUB_BLOG_TOKEN")
    BLOG_REPO: str = Field(..., env="BLOG_REPO")

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class GoogleSettings(BaseSettings):
    GOOGLE_ANALYTICS_ID: str = Field(..., env="GOOGLE_ANALYTICS_ID")
    GOOGLE_ANALYTICS_DOMAIN: str = Field(..., env="GOOGLE_ANALYTICS_DOMAIN")
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class CloudFlareSettings(BaseSettings):
    EMAIL: str = Field(..., env="CLOUDFLARE_EMAIL")
    TOKEN: str = Field(..., env="CLOUDFLARE_TOKEN")
    X_CLIENT_SECRET_TOKEN: str = Field(..., env="X_CLIENT_SECRET_TOKEN")

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class Settings(BaseSettings):
    EMAIL_SETTINGS: EmailSettings = EmailSettings()

    SECRET_KEY: str = Field(..., env="SECRET_TOKEN")

    DATABASE_SETTINGS: DatabaseSettings = DatabaseSettings()
    DEVELOPMENT_SERVER_NAME: str = Field(..., env="DEVELOPMENT_SERVER_NAME")
    LOGGING: Logging = Logging()
    DEBUG: bool = True
    GATEWAY_SETTINGS: GatewaySettings = GatewaySettings()
    SERVER_NAME: str = Field(default_factory=lambda: get_server_name())
    APPLICATION_ROOT: str = Field(default="/")
    PREFERRED_URL_SCHEME: str = Field(default="https://")
    GOOGLE_SETTINGS: GoogleSettings = GoogleSettings()
    GITHUB_SETTINGS: GithubSettings = GithubSettings()
    SEARCH_CONSOLE_API_KEY: str = Field(..., env="SEARCH_CONSOLE_API_KEY")
    EOD_STOCK_API_KEY: str = Field(..., env="EOD_STOCK_API_KEY")
    HOST_ADDRESSES: str = Field(..., env='HOST_ADDRESSES')
    CLOUDFLARE_SETTINGS: CloudFlareSettings = CloudFlareSettings()

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


@functools.lru_cache
def config_instance():
    return Settings()
