from datetime import datetime

from pydantic import BaseModel, HttpUrl


class Article(BaseModel):
    title: str
    link: HttpUrl
    summary: str
    published_at: datetime

    content: str | None = None
