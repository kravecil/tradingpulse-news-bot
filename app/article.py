from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    title: str
    link: str
    summary: str
    published_at: datetime
    content: str | None = None
