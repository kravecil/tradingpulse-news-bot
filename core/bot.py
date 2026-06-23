import logging

from maxapi import Bot
from maxapi.exceptions import MaxApiError

from config.settings import settings

logger = logging.getLogger(__name__)


class TradingPulseBot:
    def __init__(self) -> None:
        self.token = settings.bot_token.get_secret_value()
        self.chat_id = settings.chat_id
        self.bot: Bot | None = None

    async def run(self) -> None:
        if self.bot is None:
            self.bot = Bot(self.token)
            logger.info("Bot initialized successfully")
        else:
            logger.warning(
                "Attempted to initialize the bot again, but it's already initialized."
            )

    async def stop(self) -> None:
        if self.bot is not None and self.bot.session is not None:
            await self.bot.session.close()

    async def send_message(self, message: str) -> None:
        if self.bot is None:
            logger.error(
                "Attempted to send a message without initializing the bot first."
            )
            return

        try:
            await self.bot.send_message(self.chat_id, text=message)
            logger.info("Message sent successfully")
        except MaxApiError as e:
            logger.error(f"Ошибка при отправке сообщения: {e!s}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке сообщения: {e!s}")
