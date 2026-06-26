from datetime import datetime
from typing import Self

import peewee
from playhouse.pwasyncio import AsyncSqliteDatabase

from app.settings import settings

db = AsyncSqliteDatabase(settings.db_sqlite)


class Article(db.Model):
    id = peewee.AutoField(primary_key=True)

    link = peewee.TextField()

    published_at = peewee.DateTimeField(unique=True)
    created_at = peewee.DateTimeField(default=datetime.now())


class DBManager:
    def __init__(self, _db: AsyncSqliteDatabase | None = None) -> None:
        self.db: AsyncSqliteDatabase = _db or db

    async def __aenter__(self) -> Self:
        if self.db is None:
            raise ValueError("Database is not initialized")

        if self.db.is_closed():
            await self.db.aconnect()
            await self.db.acreate_tables([Article])
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.db:
            if not self.db.is_closed():
                await self.db.aclose()
                await self.db.close_pool()


class ArticleRepository:
    def __init__(self, manager: DBManager) -> None:
        self.manager = manager

    async def get_articles_by_pub_date(self, dates: list[datetime]) -> list[Article]:
        query = Article.select().where(Article.published_at.in_(dates))

        articles = await self.manager.db.list(query)

        return articles  # type: ignore

    async def create_article(self, published_at: datetime, link: str) -> Article:
        async with self.manager.db.atomic():
            article = await Article.acreate(published_at=published_at, link=link)

        return article  # type: ignore

    async def clear_articles(self) -> None:
        await self.manager.db.aexecute(Article.delete())
