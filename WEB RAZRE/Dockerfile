# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем зависимости системы для psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY app/requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY app/ .

# Экспортируем порт Flask
EXPOSE 4996

# Команда запуска
CMD ["python", "main.py"]