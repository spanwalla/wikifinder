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


class RedirectBase(BaseModel):
    source_page_id: int
    target_page_id: int


class RedirectCreate(RedirectBase):
    pass


class Redirect(RedirectBase):
    class Config:
        from_attributes = True


class QueryBase(BaseModel):
    start_page_id: int
    end_page_id: int
    execution_time: float
    paths: int


class QueryCreate(QueryBase):
    pass


class Query(QueryBase):
    id: int
    created_at: datetime
    start_page_title: str
    end_page_title: str

    class Config:
        from_attributes = True
