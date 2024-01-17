from typing import List, Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

# Assuming you have a 'models' module with 'Assign' and 'Base' defined
from models import Assign, Base
from database import SessionLocal, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AssignBase(BaseModel):
    title: str
    content: str
    isvideo: bool


class AssignResponse(BaseModel):
    id: int
    title: str
    content: str
    isvideo: bool
    time: datetime


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/assigns", response_model=List[AssignResponse])
async def get_all_assigns(db: Session = Depends(get_db)):
    assigns = db.query(Assign).all()
    return assigns


@app.post("/assigns", response_model=AssignBase)
async def create_assign(assign: AssignBase, db: Session = Depends(get_db)):
    # Set the time field to the current time on the server side
    assign_data = assign.dict()
    assign_data["time"] = datetime.now()

    db_assign = Assign(**assign_data)
    db.add(db_assign)
    db.commit()
    db.refresh(db_assign)
    return db_assign


@app.put("/assigns/{assign_id}", response_model=AssignBase)
async def update_assign(assign_id: int, updated_assign: AssignBase, db: Session = Depends(get_db)):
    db_assign = db.query(Assign).filter(Assign.id == assign_id).first()
    if not db_assign:
        raise HTTPException(status_code=404, detail="Assign not found")

    for field, value in updated_assign.dict(exclude_unset=True).items():
        setattr(db_assign, field, value)

    db_assign.time = datetime.now()

    db.commit()
    db.refresh(db_assign)

    return db_assign

@app.delete("/assigns/{assign_id}", response_model=dict)
async def delete_assign(assign_id: int, db: Session = Depends(get_db)):
    db_assign = db.query(Assign).filter(Assign.id == assign_id).first()
    
    if not db_assign:
        raise HTTPException(status_code=404, detail="Assign not found")
    
    db.delete(db_assign)
    db.commit()
    
    return {"message": "Assign deleted successfully"}