from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db

def get_db_session(db: Session = Depends(get_db)):
    return db