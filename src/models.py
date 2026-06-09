from dataclasses import dataclass


@dataclass
class Article:
    date: str
    source: str
    title: str
    description: str
    url: str
