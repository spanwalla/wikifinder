from typing import List
from pydantic import BaseModel
from datetime import datetime


class PageBase(BaseModel):
    id: int
    title: str
    is_redirect: bool


class PageCreate(PageBase):
    pass


class Page(PageBase):
    outgoing_links: List[int] = []
    incoming_links: List[int] = []

    class Config:
        from_attributes = True


class PageLinkBase(BaseModel):
    page_from: int


class PageLinkCreate(PageLinkBase):
    target_title: str


class PageLink(PageLinkBase):
    id: int
    page_target: int

    class Config:
        from_attributes = True


class QueryBase(BaseModel):
    start_page: int
    end_page: int
    execution_time: float


class QueryCreate(QueryBase):
    pass


class Query(QueryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
