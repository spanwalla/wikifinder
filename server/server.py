from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import time

from . import crud, models, schemas
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


@app.get("/")
async def root():
    return {"dump": "24-04-2024"}


@app.get("/route")
async def find_shortest_route(source: int, destination: int, db: Session = Depends(get_db)):
    start = time.time()
    db_query = crud.get_page_by_id(db, source)
    if db_query is None:
        raise HTTPException(status_code=404, detail="Page not found")
    links = db_query.links
    end = time.time()

    # query = schemas.QueryCreate(start_page=source, end_page=destination, execution_time=end-start)
    # crud.create_query(db=db, item=query)

    return {"route": [source, destination],
            "time": end - start,
            "links": links}


@app.get("/query/{query_id}", response_model=schemas.Query)
async def read_query(query_id: int, db: Session = Depends(get_db)):
    db_query = crud.get_query_by_id(db, query_id)
    if db_query is None:
        raise HTTPException(status_code=404, detail="Query not found")

    return db_query
