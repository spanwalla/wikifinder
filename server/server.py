from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import time

from . import crud, models, schemas, mitm
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    raise HTTPException(500, "Database error occurred.")


@app.get("/")
async def root():
    return {"dump": "01-05-2024"}


@app.get("/route/")
async def get_shortest_route(source: int, destination: int, db: Session = Depends(get_db)):
    if not (crud.page_exists(db, source) and crud.page_exists(db, destination)):
        raise HTTPException(404, "Page doesn't exist.")

    correct_source_id = crud.get_correct_page_id(db, source)
    correct_destination_id = crud.get_correct_page_id(db, destination)

    start = time.time()
    routes = mitm.find_shortest_route(db, correct_source_id, correct_destination_id)
    end = time.time()

    query = schemas.QueryCreate(start_page_id=correct_source_id, end_page_id=correct_destination_id,
                                execution_time=end - start, paths=len(routes))
    crud.create_query(db=db, item=query)

    return {"routes": routes,
            "time": end - start}


@app.get("/titles/")
async def get_page_titles(pages: Annotated[list[int], Query(alias="p")], db: Session = Depends(get_db)):
    crud.read_page_titles(db, pages)
    return {"result": crud.read_page_titles(db, pages)}


@app.get("/queries/", response_model=list[schemas.Query])
async def get_queries(limit: int = 10, db: Session = Depends(get_db)):
    queries = crud.read_last_queries(db, limit)
    return queries
