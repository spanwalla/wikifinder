from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

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
    query = schemas.QueryCreate(start_page=source, end_page=destination, execution_time=0.5)
    crud.create_query(db=db, item=query)
    return {"route": [source, destination],
            "time": 399,
            "start": crud.get_page_by_id(db, source)}


@app.get("/query/{query_id}", response_model=schemas.Query)
async def read_query(query_id: int, db: Session = Depends(get_db)):
    db_query = crud.get_query_by_id(db, query_id)
    if db_query is None:
        raise HTTPException(status_code=404, detail="Query not found")

    return db_query
