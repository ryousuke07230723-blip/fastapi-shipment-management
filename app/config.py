# .envを読み込んでPythonで使える形に整形
from pydantic_settings import BaseSettings, SettingsConfigDict

# .envの読み込みルール（共通設定）
# 先頭の _ は「このファイル内だけで使う」という慣習
_base_config = SettingsConfigDict(
    env_file=".env",
    env_ignore_empty=True,  # 空の値は無視
    extra="ignore",  # .envに余分な項目があっても無視
)


# BaseSettings を継承すると .env の値を自動で読み込んでくれる
class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int

    model_config = _base_config

    @property
    def POSTGRES_URL(self):
        # 各フィールドを組み合わせて接続URLを生成
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class SecuritySettings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = _base_config


class NotificationSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = _base_config


# クラスをインスタンス化して実際に使えるようにする
db_settings = DatabaseSettings()  # type: ignore

security_settings = SecuritySettings()  # type: ignore

notification_settings = NotificationSettings()  # type: ignore
