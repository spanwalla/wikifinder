from typing import Collection

from sqlalchemy import exists, desc
from sqlalchemy.orm import Session
from . import models, schemas


def split_links(links: str, sep: str = ",") -> list[int]:
    if links == "-":
        return []
    return list(map(int, links.split(sep)))


def page_exists(db: Session, page_id: int) -> bool:
    return db.query(exists().where(models.Page.id == page_id)).scalar()


def get_correct_page_id(db: Session, page_id: int) -> int:
    page = db.query(models.Page.id, models.Page.is_redirect).filter(models.Page.id == page_id).first()
    if page.is_redirect:
        redirect = db.query(models.Redirect.target_page_id).filter(models.Redirect.source_page_id == page.id).scalar()
        return redirect
    return page.id


def read_page_titles(db: Session, pages: Collection[int]) -> dict[int, str]:
    query = db.query(models.Page.id, models.Page.title).filter(models.Page.id.in_(pages))
    return dict(query.all())


def read_incoming_links(db: Session, pages: Collection[int]) -> dict[int, list[int]]:
    res = db.query(models.PageLink.page_id, models.PageLink.incoming_links).filter(models.PageLink.page_id.in_(pages))
    return {page: split_links(links) for page, links in res.all()}


def read_outgoing_links(db: Session, pages: Collection[int]) -> dict[int, list[int]]:
    res = db.query(models.PageLink.page_id, models.PageLink.outgoing_links).filter(models.PageLink.page_id.in_(pages))
    return {page: split_links(links) for page, links in res.all()}


def create_query(db: Session, item: schemas.QueryCreate) -> models.Query:
    db_query = models.Query(start_page_id=item.start_page_id, end_page_id=item.end_page_id,
                            execution_time=item.execution_time, paths=item.paths)
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query


def read_last_queries(db: Session, limit: int = 10):
    queries = db.query(models.Query).order_by(desc(models.Query.id)).limit(limit).all()
    result = []
    for query in queries:
        result.append(schemas.Query(id=query.id, start_page_id=query.start_page_id,
                                    start_page_title=query.start_page.title, end_page_id=query.end_page_id,
                                    end_page_title=query.end_page.title, created_at=query.created_at,
                                    execution_time=query.execution_time, paths=query.paths))

    return result
