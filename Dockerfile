FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings.prod \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r cooplink && useradd -r -g cooplink cooplink

COPY requirements.production.txt .
RUN pip install --no-cache-dir -r requirements.production.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R cooplink:cooplink /app

USER cooplink

RUN python manage.py collectstatic --noinput

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check --deploy || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "sync", "--timeout", "120", "core.wsgi:application"]
