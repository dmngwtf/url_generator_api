from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@postgres:5432/url_shortener"
    REDIS_URL: str = "redis://redis:6379/0"
    BASE_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "your-secret-key"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()