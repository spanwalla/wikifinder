from sqlalchemy import func, text
from sqlalchemy.orm import Session
from . import models, schemas


def get_page_by_id(db: Session, page_id: int):
    return db.query(models.Page).filter(models.Page.id == page_id).first()


def get_page_id_by_title(db: Session, page_title: str):
    return db.execute(text('SELECT id FROM pages WHERE title = :page_title LIMIT 1'),
                      {"page_title": page_title}).scalar()
    # return db.query(models.Page).filter(func.match(models.Page.title, page_title)).first()


def create_query(db: Session, item: schemas.QueryCreate):
    db_query = models.Query(start_page=item.start_page, end_page=item.end_page, execution_time=item.execution_time)
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query


def get_query_by_id(db: Session, query_id: int):
    return db.query(models.Query).filter(models.Query.id == query_id).first()
