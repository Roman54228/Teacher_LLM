# Dockerfile для Telegram Mini App
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    nano \
    htop \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements-production.txt .
COPY pyproject.toml .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements-production.txt

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p logs static data

# Установка прав доступа
RUN chmod +x main.py

# Переменные окружения
ENV PYTHONPATH=/app
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5002

# Открытие порта
EXPOSE 5002

# Команда по умолчанию (можно переопределить)
CMD ["python", "main.py"]