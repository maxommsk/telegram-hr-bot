# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для приложения
RUN useradd --create-home --shell /bin/bash app

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY src/ ./src/
COPY .env.example .env

# Создаем необходимые директории
RUN mkdir -p logs uploads && \
    chown -R app:app /app

# Переключаемся на пользователя приложения
USER app

# Открываем порт
EXPOSE 5000

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

# Команда для запуска приложения
CMD ["python", "src/main.py"]

