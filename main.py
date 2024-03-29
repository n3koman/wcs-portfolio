from typing import List, Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

# Assuming you have aaaaaaa 'models' module with 'Assign' and 'Base' defined
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
    videoContent: str


class AssignResponse(BaseModel):
    id: int
    title: str
    content: str
    videoContent: str
    time: datetime

def utc_to_local(utc_dt):
    # Create a fixed offset for GMT+6 (6 hours ahead of UTC)
    gmt_plus_6 = timezone(timedelta(hours=6))
    
    # Apply the offset to the UTC datetime
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=gmt_plus_6)
    
    return local_dt

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
    assign_data["time"] = utc_to_local(datetime.utcnow())

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

    db_assign.time = utc_to_local(datetime.utcnow())

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
