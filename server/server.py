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
    return {"route": [source, destination],
            "time": 399}
