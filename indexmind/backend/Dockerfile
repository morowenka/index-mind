
# Базовый образ, slim и с фиксированной версией
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка системных зависимостей с очисткой мусора
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
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
COPY .env .env

RUN export $(cat .env | xargs)

# Запуск тестов во время сборки
RUN pip install pytest && pytest

# Создаем и переключаемся на пользователя без прав root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

VOLUME ["/app/data", "/app/config", "/app/logs"]

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Открываем только один порт, который реально используется
EXPOSE 8000

ENTRYPOINT ["uvicorn"]
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]