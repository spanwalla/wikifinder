from typing import Collection
from sqlalchemy.orm import Session
from . import models, schemas


def split_links(links: str, sep: str = ",") -> list[int]:
    if links == "-":
        return []
    return list(map(int, links.split(sep)))


def read_page_by_id(db: Session, page_id: int) -> models.Page:
    return db.query(models.Page).filter(models.Page.id == page_id).first()


def read_incoming_links(db: Session, pages: Collection[int]) -> dict[int, list[int]]:
    res = db.query(models.PageLink.page_id, models.PageLink.incoming_links).filter(models.PageLink.page_id.in_(pages))
    return {page: split_links(links) for page, links in res.all()}


def read_outgoing_links(db: Session, pages: Collection[int]) -> dict[int, list[int]]:
    res = db.query(models.PageLink.page_id, models.PageLink.outgoing_links).filter(models.PageLink.page_id.in_(pages))
    return {page: split_links(links) for page, links in res.all()}


def create_query(db: Session, item: schemas.QueryCreate) -> models.Query:
    db_query = models.Query(start_page=item.start_page, end_page=item.end_page, execution_time=item.execution_time,
                            paths=item.paths)
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query
