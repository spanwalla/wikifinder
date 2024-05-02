from pydantic import BaseModel


class PageBase(BaseModel):
    title: str


class PageCreate(PageBase):
    pass


class Page(PageBase):
    id: int

    class Config:
        orm_mode = True
