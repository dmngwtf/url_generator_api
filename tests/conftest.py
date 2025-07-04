import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.config import Settings
from app.models.url import URL  
from app.models.user import User 
from unittest.mock import MagicMock

# Settings for SQLite test database
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    # Sqlite engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    
    print("Registered tables in Base.metadata before create_all:", list(Base.metadata.tables.keys()))
    
    # Создание табличек
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables created in database:", tables)
    assert "urls" in tables, f"Table 'urls' was not created. Registered tables: {list(Base.metadata.tables.keys())}"
    assert "users" in tables, f"Table 'users' was not created. Registered tables: {list(Base.metadata.tables.keys())}"
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            print("Tables in session:", [row[0] for row in result])
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Сброс табличек после тестов
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped after test")

# FastAPi фикстура
@pytest.fixture
def client(test_db):
    return TestClient(app)

# Редис фикстура
@pytest.fixture
def mock_redis(mocker):
    mock = MagicMock()
    mocker.patch("app.services.url_service.redis_client", mock)
    return mock

#Фикстура для конфигурации настроек 
@pytest.fixture
def settings():
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        REDIS_URL="redis://localhost:6379/0",
        BASE_URL="http://localhost:8000",
        SECRET_KEY="test-secret-key",
        REDIS_TTL=3600
    )