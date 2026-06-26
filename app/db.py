from datetime import datetime
from typing import Self

import peewee
from playhouse.pwasyncio import AsyncSqliteDatabase

from app.settings import settings

db = AsyncSqliteDatabase(settings.db_sqlite)


class Article(db.Model):
    id = peewee.AutoField(primary_key=True)
    guid = peewee.IntegerField(unique=True)

    published_at = peewee.DateTimeField()
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

    async def get_articles_by_guids(self, guids: list[int]) -> list[Article]:
        query = Article.select().where(Article.guid.in_(guids))

        articles = await self.manager.db.list(query)

        return articles  # type: ignore

    async def create_article(self, guid: int, published_at: datetime) -> Article:
        async with self.manager.db.atomic():
            article = await Article.acreate(guid=guid, published_at=published_at)

        return article  # type: ignore

    async def clear_articles(self) -> None:
        await self.manager.db.aexecute(Article.delete())
