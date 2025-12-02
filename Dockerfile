# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Создаем директории для данных, если их нет
RUN mkdir -p images conspects

# Открываем порт
EXPOSE 8000

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV DOCKER_CONTAINER=true

# Скрипт инициализации (опционально запускает миграцию)
COPY migrate_to_db.py .

# Команда запуска
CMD ["python", "server.py"]

