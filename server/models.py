from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    is_redirect = Column(Boolean, default=False)
    outgoing_links = relationship("PageLink", foreign_keys="[PageLink.page_from]", backref="source_page")
    incoming_links = relationship("PageLink", foreign_keys="[PageLink.page_target]", backref="target_page")


class PageLink(Base):
    __tablename__ = "pagelinks"

    id = Column(Integer, primary_key=True)
    page_from = Column(Integer, ForeignKey("pages.id"))
    page_target = Column(Integer, ForeignKey("pages.id"))


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    start_page = Column(Integer, ForeignKey("pages.id"))
    end_page = Column(Integer, ForeignKey("pages.id"))
    execution_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
