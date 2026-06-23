from maxapi import Bot
from maxapi.enums import ParseMode

from app.settings import settings

bot = Bot(token=settings.bot_token.get_secret_value(), parse_mode=ParseMode.MARKDOWN)
