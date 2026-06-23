from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    title: str
    link: str
    summary: str
    published_at: datetime
    source: str
    category: str
    content: str

    summary_ru: str | None = None
    sentiment: str | None = None
