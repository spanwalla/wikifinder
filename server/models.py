from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    is_redirect = Column(Boolean, default=False)
    links = relationship("PageLink", foreign_keys="[PageLink.page_id]", backref="page")


class PageLink(Base):
    __tablename__ = "pagelinks"

    page_id = Column(Integer, ForeignKey("pages.id"), primary_key=True)
    incoming_links = Column(Text, default="-")
    outgoing_links = Column(Text, default="-")


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    start_page = Column(Integer, ForeignKey("pages.id"))
    end_page = Column(Integer, ForeignKey("pages.id"))
    execution_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
