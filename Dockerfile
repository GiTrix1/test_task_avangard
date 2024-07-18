# Используем образ Python
FROM python:3.8

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и исходный код в контейнер
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Команда для запуска скрипта при старте контейнера
CMD ["python", "crypto_tracker.py"]