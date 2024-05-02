from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    title = Column(String)


# class Query(Base):
#     __tablename__ = "queries"
#
#     id = Column(Integer, primary_key=True)
#     source = Column(Integer, ForeignKey("pages.id"))
#     destination = Column(Integer, ForeignKey("pages.id"))
#     execution_time = Column()
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
