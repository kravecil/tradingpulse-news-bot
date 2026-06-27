# TradingPulse News MAX BOT

Бот-агргатор новостей с информационных площадок. Бот получает список новостей с RSS ленты, отфильтровывает существующие в базе данных, а новые прогоняет через YandexGPT и постит в канал мессенджера. 

Поддерживаемые площадки (будут добавляться):
- [cointelegraph.com](https://cointelegraph.com/)

Поддерживаемые мессенджеры (будут добавляться):
- [МАКС](https://max.ru/)


## Установка и деплой

Требуется: [Docker](https://www.docker.com/)

1.  **Клонировать репозиторий**:
    ```bash
    git clone https://github.com/your-username/tradingpulse-news.git
    cd tradingpulse-news
    ```

2.  **Сконфигурировать переменные окружения**:
    ```bash
    cp .env.example .env
    # Отредактируйте .env своими значениями
    ```

    *   `BOT_TOKEN`: Ваш токен бота.
    *   `CHAT_ID`: Идентификатор канала, куда отправлять посты.
    *   `YANDEX_API_KEY` & `YANDEX_FOLDER_ID`: Ваши учётные данные Yandex Cloud для доступа к Yandex GPT.

4.  **Сборка и запуск**:
    ```bash
    docker compose up -d --build
    ```
