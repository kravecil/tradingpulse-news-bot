import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from core.application import TradingPulseApplication

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    """Контекстный менеджер для управления жизненным циклом приложения."""
    app = TradingPulseApplication()

    try:
        await app.initialize()
        yield app
    finally:
        await app.shutdown()


async def main():
    """Точка входа приложения."""

    # Создание и запуск приложения
    async with lifespan() as app:
        await app.run()


if __name__ == "__main__":
    # Запуск приложения
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение завершено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e!s}")
        sys.exit(1)
