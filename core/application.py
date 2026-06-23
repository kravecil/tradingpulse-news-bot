import asyncio
import logging
import signal

from core.bot import TradingPulseBot

logger = logging.getLogger(__name__)


class TradingPulseApplication:
    def __init__(self) -> None:
        self.bot: TradingPulseBot | None = None

        self.is_running = False
        self.shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        """Инициализировать все компоненты приложения."""
        logger.info("Инициализация приложения...")

        try:
            # Инициализация бота
            self.bot = TradingPulseBot()
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e!s}")
            await self.shutdown()
            raise

    async def run(self) -> None:
        """Запустить приложение."""
        if self.is_running:
            logger.warning("Приложение уже запущено")
            return

        self.is_running = True
        logger.info("Запуск приложения...")

        # Запуск бота
        bot_task = asyncio.create_task(self._run_bot(), name="telegram_bot")

        logger.info("Приложение запущено. Ожидание сигнала завершения...")
        await self.shutdown_event.wait()

        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            logger.info("Задача бота отменена")

        logger.info("Приложение остановлено корректно")

        try:
            # Настройка обработчиков сигналов
            self._setup_signal_handlers()

        except Exception as e:
            logger.error(f"Ошибка во время работы приложения: {e!s}")
            await self.shutdown()
            raise

    async def _run_bot(self):
        """Запустить бота."""
        try:
            await self.bot.run()
        except asyncio.CancelledError:
            logger.info("Бот остановлен по запросу")
        except Exception as e:
            logger.error(f"Критическая ошибка в работе бота: {e!s}", exc_info=True)

    def _setup_signal_handlers(self):
        """Настроить обработчики сигналов для graceful shutdown."""
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda s=sig: asyncio.create_task(self._handle_shutdown_signal(s))
            )
        logger.info("Обработчики сигналов настроены")

    async def _handle_shutdown_signal(self, sig):
        """Обработать сигнал завершения."""
        logger.info(f"Получен сигнал {sig.name}. Инициируется остановка...")
        self.shutdown_event.set()

    async def shutdown(self) -> None:
        """Корректно завершить работу всех компонентов."""
        if not self.is_running:
            return

        logger.info("Начало завершения работы приложения...")

        self.is_running = False
        self.shutdown_event.set()

        logger.info("Приложение полностью остановлено")
