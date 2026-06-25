import logging

from maxapi import Bot as MaxBot
from maxapi.enums import ParseMode

from app.settings import settings

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self) -> None:
        if not settings.bot_token:
            raise ValueError("Missing bot token configuration")

        token = settings.bot_token.get_secret_value()
        if not token:
            raise ValueError("Bot token must not be empty")

        self.bot = MaxBot(token=token, parse_mode=ParseMode.MARKDOWN)
        self.chat_id = settings.chat_id

        self.maximum_message_length = settings.maximum_message_length

    async def send(self, text: str | None) -> None:
        if text is None:
            return

        text = text[: self.maximum_message_length]

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e!s}")


def create_bot() -> Bot:
    return Bot()
