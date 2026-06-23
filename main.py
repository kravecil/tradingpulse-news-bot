import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)


async def main():
    logger.info("Запуск приложения...")


if __name__ == "__main__":
    # Запуск приложения
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение завершено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e!s}")
        sys.exit(1)
