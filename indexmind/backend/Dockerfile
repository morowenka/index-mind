# Базовый образ, slim и с фиксированной версией
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка системных зависимостей с очисткой мусора
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем только requirements для лучшего кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data /app/config /app/logs

# Копируем только нужные файлы
COPY src/ src/
COPY tests/ tests/
COPY schemas/ schemas/
COPY config/ config/
COPY app.py .
COPY pytest.ini .

# Создаем и переключаемся на пользователя без прав root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Документируем порт из переменной среды
EXPOSE ${PORT:-8000}

# Используем переменную окружения PORT с дефолтным значением 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]