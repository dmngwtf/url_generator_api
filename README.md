
---

# Микросервис для сокращения URL

*A microservice for shortening URLs using FastAPI, PostgreSQL, and Redis*

---

##  Технологии / Technologies

* **FastAPI** — Асинхронный HTTP-сервер
  *Asynchronous HTTP server*
* **SQLAlchemy** — ORM для работы с базой данных
  *ORM for database operations*
* **Alembic** — Миграции базы данных
  *Database migrations*
* **Pydantic** — Валидация данных
  *Data validation*
* **Redis** — Кэширование
  *Caching*
* **PostgreSQL** — Хранилище данных
  *Data storage*
* **Docker / Docker Compose** — Контейнеризация
  *Containerization*
* **xxHash / base62** — Генерация коротких ключей
  *Short key generation*
* **Uvicorn / Gunicorn** — Запуск сервера
  *ASGI server launch*

---

##  Запуск / Running

### 1. Клонируйте репозиторий

*Clone the repository:*

```bash
git clone https://github.com/dmngwtf/url_generator_api
cd url_shortener
```

### 2. Создайте `.env` файл

*Create a `.env` file (see `.env.example`).*

### 3. Запустите сервисы

*Start the services:*

```bash
docker-compose up -d --build
```

### 4. Примените миграции

*Apply database migrations:*

```bash
docker-compose exec app alembic upgrade head
```

---

##  Использование / Usage

###  Создать короткий URL

*Create a short URL:*

```bash
curl -X POST "http://localhost:8000/shorten" \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://example.ru"}'
```

###  Перейти по короткому URL

*Redirect using the short URL:*

```bash
curl http://localhost:8000/<short_key>
```

---

