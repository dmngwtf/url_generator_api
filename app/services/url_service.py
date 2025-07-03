import xxhash
import base62
import redis
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.url import URL
from app.schemas.url import URLCreate, URLResponse
from app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def generate_short_key(url: str) -> str:
    hash_object = xxhash.xxh64()
    hash_object.update(str(url).encode('utf-8'))  # Преобразуем url в строку
    hash_int = hash_object.intdigest()
    return base62.encode(hash_int)[:8]

def create_short_url(db: Session, url: URLCreate, user_id: int = None) -> URLResponse:
    short_key = generate_short_key(url.original_url)
    
    # Проверка коллизии
    existing_url = db.query(URL).filter(URL.short_key == short_key).first()
    if existing_url:
        raise HTTPException(status_code=400, detail="Short key collision")
    
    db_url = URL(
        original_url=str(url.original_url),  # Преобразуем HttpUrl в строку
        short_key=short_key,
        user_id=user_id
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    # Кеширование
    redis_client.setex(f"url:{short_key}", 3600, db_url.original_url)
    
    return URLResponse(
        original_url=db_url.original_url,
        short_key=db_url.short_key,
        short_url=f"{settings.BASE_URL}/{db_url.short_key}",
        created_at=db_url.created_at,
        user_id=db_url.user_id
    )

def get_original_url(db: Session, short_key: str) -> str:
    # Проверка кеша
    cached_url = redis_client.get(f"url:{short_key}")
    if cached_url:
        return cached_url
    
    # Поиск в БД
    db_url = db.query(URL).filter(URL.short_key == short_key).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Обновление кеша
    redis_client.setex(f"url:{short_key}", 3600, db_url.original_url)
    return db_url.original_url