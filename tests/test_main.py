import pytest
from fastapi.testclient import TestClient
from sqlalchemy.sql import text
from app.models.url import URL
from app.schemas.url import URLCreate

@pytest.mark.asyncio
async def test_check_tables(test_db):
    result = test_db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    table_names = [row[0] for row in result]
    print("Tables in test_check_tables:", table_names)
    assert "urls" in table_names, "Table 'urls' was not created"
    assert "users" in table_names, "Table 'users' was not created"

@pytest.mark.asyncio
async def test_create_short_url(client: TestClient, test_db, mock_redis):
    # Отладочный вывод для проверки таблиц
    result = test_db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    table_names = [row[0] for row in result]
    print("Tables in test_create_short_url:", table_names)
    
    # Подготавливаем данные
    payload = {"original_url": "https://example.com"}
    
    # Мокаем Redis
    mock_redis.setex.return_value = True
    
    # Выполняем запрос
    response = client.post("/shorten", json=payload)
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert data["original_url"].rstrip("/") == "https://example.com"
    assert data["short_key"]
    assert data["short_url"].startswith("http://localhost:8000/")
    assert "created_at" in data
    assert data["user_id"] is None
    
    # Проверяем базу данных
    db_url = test_db.query(URL).filter(URL.short_key == data["short_key"]).first()
    assert db_url is not None
    assert db_url.original_url.rstrip("/") == "https://example.com"
    
    # Проверяем вызов Redis
    mock_redis.setex.assert_called_once()

@pytest.mark.asyncio
async def test_create_short_url_invalid_url(client: TestClient, test_db):
    # Отладочный вывод для проверки таблиц
    result = test_db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    table_names = [row[0] for row in result]
    print("Tables in test_create_short_url_invalid_url:", table_names)
    
    # Проверяем невалидный URL
    payload = {"original_url": "not-a-valid-url"}
    response = client.post("/shorten", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_redirect_url(client: TestClient, test_db, mock_redis):
    # Отладочный вывод для проверки таблиц
    result = test_db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    table_names = [row[0] for row in result]
    print("Tables in test_redirect_url:", table_names)
    
    # Создаем тестовую запись
    short_key = "test123"
    original_url = "https://example.com"
    db_url = URL(original_url=original_url, short_key=short_key)
    test_db.add(db_url)
    test_db.commit()
    
    # Мокаем Redis
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    
    # Выполняем запрос
    response = client.get(f"/{short_key}", follow_redirects=False)
    
    # Проверяем редирект
    assert response.status_code == 307  # Temporary Redirect
    assert response.headers["location"] == original_url
    
    # Проверяем вызовы Redis
    mock_redis.get.assert_called_once_with(f"url:{short_key}")
    mock_redis.setex.assert_called_once_with(f"url:{short_key}", 3600, original_url)

@pytest.mark.asyncio
async def test_redirect_url_not_found(client: TestClient, test_db, mock_redis):
    # Отладочный вывод для проверки таблиц
    result = test_db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    table_names = [row[0] for row in result]
    print("Tables in test_redirect_url_not_found:", table_names)
    
    mock_redis.get.return_value = None
    
    # Проверяем несуществующий ключ
    response = client.get("/nonexistent", follow_redirects=False)
    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"