import pytest
from app.services.url_service import generate_short_key, create_short_url, get_original_url
from app.schemas.url import URLCreate
from app.models.url import URL
from fastapi import HTTPException
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_generate_short_key():
    url = "https://example.com"
    short_key = generate_short_key(url)
    assert len(short_key) <= 8
    assert short_key == generate_short_key(url)  # Проверяем детерминированность

@pytest.mark.asyncio
async def test_create_short_url(test_db, mock_redis, settings):
    # Подготавливаем данные
    url_create = URLCreate(original_url="https://example.com")
    mock_redis.setex.return_value = True
    
    # Выполняем создание URL
    result = create_short_url(test_db, url_create)
    
    # Проверяем результат (учитываем возможный завершающий слеш)
    assert result.original_url.rstrip("/") == "https://example.com"
    assert result.short_key
    assert result.short_url == f"{settings.BASE_URL}/{result.short_key}"
    
    # Проверяем БД
    db_url = test_db.query(URL).filter(URL.short_key == result.short_key).first()
    assert db_url is not None
    assert db_url.original_url.rstrip("/") == "https://example.com"
    
    # Проверяем Redis
    mock_redis.setex.assert_called_once()

@pytest.mark.asyncio
async def test_create_short_url_collision(test_db, mock_redis, mocker):
    # Мокаем generate_short_key для создания коллизии
    mocker.patch("app.services.url_service.generate_short_key", return_value="test123")
    
    # Создаем первую запись
    url_create = URLCreate(original_url="https://example.com")
    create_short_url(test_db, url_create)
    
    # Пытаемся создать еще одну с тем же ключом
    with pytest.raises(HTTPException) as exc:
        create_short_url(test_db, url_create)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Short key collision"

@pytest.mark.asyncio
async def test_get_original_url_from_cache(mock_redis):
    # Мокаем Redis
    mock_redis.get.return_value = "https://example.com"
    
    # Проверяем получение из кеша
    result = get_original_url(MagicMock(), "test123")
    assert result == "https://example.com"
    mock_redis.get.assert_called_once_with("url:test123")

@pytest.mark.asyncio
async def test_get_original_url_from_db(test_db, mock_redis):
    # Мокаем Redis (пустой кеш)
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    
    # Создаем запись в БД
    short_key = "test123"
    original_url = "https://example.com"
    db_url = URL(original_url=original_url, short_key=short_key)
    test_db.add(db_url)
    test_db.commit()
    
    # Проверяем получение из БД
    result = get_original_url(test_db, short_key)
    assert result == original_url
    mock_redis.setex.assert_called_once_with(f"url:{short_key}", 3600, original_url)

@pytest.mark.asyncio
async def test_get_original_url_not_found(test_db, mock_redis):
    # Мокаем Redis (пустой кеш)
    mock_redis.get.return_value = None
    
    # Проверяем несуществующий ключ
    with pytest.raises(HTTPException) as exc:
        get_original_url(test_db, "nonexistent")
    assert exc.value.status_code == 404
    assert exc.value.detail == "URL not found"