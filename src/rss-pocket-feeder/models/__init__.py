from pydantic.dataclasses import dataclass

@dataclass
class RSSItem:
    link: str

@dataclass
class PocketItem:
    link: str
    item_id: int

@dataclass
class FeedPostRequest:
    rss_link: str
