# TradingPulse News MAX BOT

A sophisticated news aggregation and distribution bot for the cryptocurrency and financial markets, built as a MAX BOT using the `maxapi` library.

This bot fetches news from various sources (RSS feeds, Reddit, DefiLlama) and uses Yandex GPT to summarize, translate, and analyze the content before sending it to a Telegram channel.

## Features

*   **Multi-Source Aggregation**: Pulls news from RSS feeds (CoinTelegraph, CoinDesk), Reddit communities, and DeFi API data.
*   **AI-Powered Processing**: Uses Yandex GPT to summarize articles in Russian and determine sentiment.
*   **Automated Telegram Distribution**: Sends curated newsletters to a designated Telegram channel at regular intervals.
*   **Configurable**: All settings (sources, intervals, AI service) are managed through a configuration file and environment variables.
*   **Modular Design**: Clean separation of concerns with distinct modules for sources, processing, and the bot logic.

## Project Structure

```
tradingpulse-news/
├── pyproject.toml           # Project configuration and dependencies
├── .env.example             # Example environment variables
├── README.md                # This file
└── src/
    └── tradingpulse_news/
        ├── __init__.py
        ├── __main__.py        # Entry point for the script
        ├── config.py          # Configuration management
        ├── bot.py             # Main bot logic and orchestration
        ├── processor.py       # AI processing with Yandex GPT
        └── sources/
            ├── base.py        # Abstract base class for sources
            ├── rss.py         # RSS feed source
            └── social.py      # Social and API sources (Reddit, DefiLlama)
```

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/tradingpulse-news.git
    cd tradingpulse-news
    ```

2.  **Create a virtual environment and install dependencies**:
    ```bash
    poetry install
    ```

3.  **Configure environment variables**:
    Copy `.env.example` to `.env` and fill in your credentials:
    ```bash
    cp .env.example .env
    # Edit .env with your values
    ```

    *   `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather.
    *   `TELEGRAM_CHAT_ID`: The ID of the Telegram channel/group to send news to.
    *   `YANDEX_FOLDER_ID` & `YANDEX_API_KEY`: Your Yandex Cloud credentials for Yandex GPT.

4.  **Run the bot**:
    ```bash
    poetry run python -m tradingpulse_news
    ```