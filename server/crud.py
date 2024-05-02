from sqlalchemy import Session
from . import models, schemas


def get_page_by_id(db: Session, page_id: int):
    return db.query(models.Page).filter(models.Page.id == page_id).first()
