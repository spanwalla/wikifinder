from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
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


@app.get("/")
async def root():
    return {"dump": "01-05-2024"}


@app.get("/route")
async def get_shortest_route(source: int, destination: int, db: Session = Depends(get_db)):
    start = time.time()
    routes = mitm.find_shortest_route(db, source, destination)
    end = time.time()

    query = schemas.QueryCreate(start_page=source, end_page=destination, execution_time=end-start, paths=len(routes))
    crud.create_query(db=db, item=query)

    return {"routes": routes,
            "time": end - start}
