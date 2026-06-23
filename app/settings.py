from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    bot_token: SecretStr = Field(
        default=...,
        description="Токен бота, например: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        examples=["123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"],
    )

    chat_id: int = Field(
        default=..., description="ID чата, например: ", examples=[-1001234567890]
    )

    yandex_api_key: SecretStr = Field(
        default=...,
        description="API-ключ для доступа к Yandex CLoud",
    )

    yandex_folder_id: str = Field(
        default=...,
        description="ID папки в Yandex Cloud",
        examples=["b1g2h3i4j5k6l7m8n9"],
    )


settings = Settings()
