# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости для WeasyPrint и других библиотек
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    libssl-dev \
    libpango1.0-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libgirepository1.0-dev \
    fonts-liberation \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements-docker.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements-docker.txt

# Копируем код приложения
COPY . .

# Создаем директорию для отчетов
RUN mkdir -p /app/research_reports

# Открываем порты для API и Streamlit
EXPOSE 8000 8502

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 