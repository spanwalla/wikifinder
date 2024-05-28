from pydantic import BaseModel
from datetime import datetime


class PageBase(BaseModel):
    id: int
    title: str
    is_redirect: bool


class PageCreate(PageBase):
    pass


class Page(PageBase):
    outgoing_links: list[int] = []
    incoming_links: list[int] = []

    class Config:
        from_attributes = True


class PageLinkBase(BaseModel):
    page_id: int
    page_from: str = "-"
    page_target: str = "-"


class PageLinkCreate(PageLinkBase):
    pass


class PageLink(PageLinkBase):
    pass

    class Config:
        from_attributes = True


class QueryBase(BaseModel):
    start_page: int
    end_page: int
    execution_time: float
    paths: int


class QueryCreate(QueryBase):
    pass


class Query(QueryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
