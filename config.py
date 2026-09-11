from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str


    @property
    def DATABASE_URL(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'



    jwt_secret_key: SecretStr
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 20

    max_upload_size_bytes: int = 5 * 1024 * 1024

    posts_per_page: int = 5

    reset_token_expire_minutes: int = 60


    MAIL_SERVER: str
    MAIL_PORT: int 
    MAIL_USE_SSL: bool
    # MAIL_START_TLS: bool
    MAIL_USERNAME: str 
    MAIL_HOST_USER: str
    MAIL_PASSWORD: SecretStr

    FRONTEND_URL: str


settings = Settings()