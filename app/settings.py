from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    bot_token: SecretStr = Field(
        description="Токен бота, например: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        examples=["123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"],
    )

    chat_id: int = Field(
        description="ID чата, например: ",
        examples=[-1001234567890],
    )

    yandex_api_key: SecretStr = Field(
        description="API-ключ для доступа к Yandex CLoud",
    )

    yandex_folder_id: str = Field(
        description="ID папки в Yandex Cloud",
        examples=["b1g2h3i4j5k6l7m8n9"],
    )

    openai_model: str = Field(
        default="yandexgpt",
        description="Модель OpenAI для генерации текста",
        examples=["gpt-4o-mini", "yandexgpt"],
    )

    openai_base_url: str = Field(
        default="https://ai.api.cloud.yandex.net/v1",
        description="Базовый URL для OpenAI API",
        examples=["https://ai.api.cloud.yandex.net/v1"],
    )

    maximum_message_length: int = Field(
        default=4096, description="Максимальная длина сообщения", examples=[4096]
    )


settings = Settings()  # type: ignore
