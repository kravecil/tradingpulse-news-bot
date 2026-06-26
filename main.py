import asyncio
import logging
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.tasks import publish

INTERVAL = 5  # minutes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    force=True,
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

shutdown_event = asyncio.Event()


async def main():
    scheduler = AsyncIOScheduler(logger=logger)
    scheduler.add_job(
        publish,
        trigger=IntervalTrigger(minutes=INTERVAL),
        id="publish_job",
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()

    logger.info("Запуск приложения...")

    await shutdown_event.wait()


if __name__ == "__main__":
    # Запуск приложения
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение завершено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e!s}")
        sys.exit(1)
