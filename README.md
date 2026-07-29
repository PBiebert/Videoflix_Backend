# Videoflix – Backend

> Video streaming platform API | REST API built with Django & Django REST Framework

Videoflix is a Netflix-style video streaming platform. This repository contains
**the backend only**, which provides user authentication, video management, and
adaptive HLS video streaming through a REST API. The corresponding frontend
communicates with this backend via these endpoints.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation & Configuration](#installation--configuration)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Frontend](#frontend)
- [Author](#author)

---

## Prerequisites

- Docker
- Docker Compose

---

## Installation & Configuration

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd Videoflix_Backend
   ```

2. Set up the `.env` file – sensitive settings are not stored directly in
   `core/settings.py` but loaded from a local `.env` file (ignored by Git):

   ```bash
   cp .env.template .env
   ```

3. Generate a new `SECRET_KEY` and add it to the `.env` file:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Fill in the remaining values in your `.env` file:

   ```env
   SECRET_KEY="your_generated_key_here"
   DEBUG=True

   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
   CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
   FRONTEND_URL=http://127.0.0.1:5500

   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=db
   DB_PORT=5432

   REDIS_HOST=redis
   REDIS_LOCATION=redis://redis:6379/1
   REDIS_PORT=6379
   REDIS_DB=0

   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email_user
   EMAIL_HOST_PASSWORD=your_email_user_password
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   DEFAULT_FROM_EMAIL=default_from_email
   ```

   > **Note:** Use `DEBUG=True` for local development only. Set it to `False` in
   > production and update `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and
   > `CSRF_TRUSTED_ORIGINS` to match your actual domain(s).

4. Build and start the containers (Django web app, PostgreSQL, Redis):

   ```bash
   docker compose up --build
   ```

   On first startup the entrypoint script automatically waits for PostgreSQL,
   applies database migrations, and creates a superuser from the
   `DJANGO_SUPERUSER_*` variables in your `.env` file.

5. Run the test suite once to verify that everything is configured correctly:

   ```bash
   docker compose exec web python manage.py test
   ```

   The API will be available at: `http://127.0.0.1:8000/`

---

## Project Structure

```
Videoflix_Backend/
├── core/                    # Django project configuration (settings, urls, wsgi, asgi)
├── accounts/                # User management & JWT cookie authentication
│   ├── api/                 # Serializers, views, URLs for accounts
│   └── tests/                # Registration, login, logout, activation, password reset tests
├── video_library/            # Video management & HLS streaming
│   ├── api/                  # Serializers, views, URLs for videos
│   ├── signals.py             # Triggers HLS conversion & cache invalidation on save/delete
│   ├── tasks.py                # Background video conversion via ffmpeg (django-rq)
│   ├── storage.py               # HLS output path resolution
│   └── tests/                    # Video list tests
├── media/                          # Uploaded videos, thumbnails & generated HLS files
├── static/                          # Collected static files
├── docs/                             # ER diagram & API documentation
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## API Endpoints

> For full endpoint documentation including request/response examples, status
> codes and permissions, see [docs/api.md](docs/api.md).

### Authentication

| Method | Endpoint                                  | Description                              | Auth required | Access          |
| ------ | ------------------------------------------ | ------------------------------------------ | -------------- | ---------------- |
| POST   | `/api/register/`                           | Register a new, inactive user              | No             | All              |
| GET    | `/api/activate/{uidb64}/{token}/`          | Activate a user account                    | No             | All              |
| POST   | `/api/login/`                              | Log in and set HttpOnly auth cookies       | No             | All              |
| POST   | `/api/token/refresh/`                      | Refresh the access token cookie            | No             | All              |
| POST   | `/api/logout/`                             | Log out and blacklist the refresh token    | Yes            | Logged-in user   |
| POST   | `/api/password_reset/`                     | Send a password-reset email                | No             | All              |
| POST   | `/api/password_confirm/{uidb64}/{token}/`  | Set a new password                         | No             | All              |

### Video Library

| Method | Endpoint                                          | Description                          | Auth required | Access          |
| ------ | --------------------------------------------------- | --------------------------------------- | -------------- | ---------------- |
| GET    | `/api/video/`                                       | List all videos                         | Yes            | Logged-in user   |
| GET    | `/api/video/{movie_id}/{resolution}/index.m3u8`     | Retrieve the HLS playlist for a video   | Yes            | Logged-in user   |
| GET    | `/api/video/{movie_id}/{resolution}/{segment}/`     | Retrieve a single HLS video segment     | Yes            | Logged-in user   |

---

## Frontend

The corresponding frontend repository can be found here:

[Frontend Repository](#) — Coming soon

---

## Author

**Philipp Biebert**  
Project status: 29.07.2026
