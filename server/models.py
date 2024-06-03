from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    is_redirect = Column(Boolean, default=False)


class PageLink(Base):
    __tablename__ = "pagelinks"

    page_id = Column(Integer, ForeignKey("pages.id"), primary_key=True)
    incoming_links = Column(Text, default="-")
    outgoing_links = Column(Text, default="-")


class Redirect(Base):
    __tablename__ = "redirects"

    source_page_id = Column(Integer, ForeignKey("pages.id"), primary_key=True)
    target_page_id = Column(Integer, ForeignKey("pages.id"), primary_key=True)


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    start_page_id = Column(Integer, ForeignKey("pages.id"))
    end_page_id = Column(Integer, ForeignKey("pages.id"))
    execution_time = Column(Float)
    paths = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    start_page = relationship("Page", foreign_keys="[Query.start_page_id]")
    end_page = relationship("Page", foreign_keys="[Query.end_page_id]")
