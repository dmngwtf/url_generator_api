from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.schemas.url import URLCreate, URLResponse
from app.services.url_service import create_short_url, get_original_url
from app.dependencies import get_db_session

app = FastAPI(title="URL Shortener Microservice")

@app.post("/shorten", response_model=URLResponse)
async def shorten_url(url: URLCreate, db: Session = Depends(get_db_session)):
    return create_short_url(db, url)

@app.get("/{short_key}")
async def redirect_url(short_key: str, db: Session = Depends(get_db_session)):
    original_url = get_original_url(db, short_key)
    return RedirectResponse(url=original_url)