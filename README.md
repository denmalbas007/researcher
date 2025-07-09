# AI Deep Researcher - Автоматический исследователь, генерация на 50+ страниц на основе информации в интернете

Интеллектуальная система для автоматического проведения исследований с использованием ИИ. Система собирает информацию из интернета, анализирует её и создает структурированные отчеты в формате PDF.
demo: http://80.74.29.175:8512/
## ✨ Возможности

- 🔍 **Автоматический поиск** - поиск релевантной информации по заданной теме
- 📄 **Анализ источников** - суммаризация найденных веб-страниц
- 📋 **Структурированные отчеты** - создание детальных отчетов с таблицами и источниками
- 📄 **PDF генерация** - красиво оформленные PDF документы
- 🌐 **Веб-интерфейс** - удобный Streamlit интерфейс
- 🚀 **API** - REST API для интеграции с другими системами
- 🐳 **Docker поддержка** - легкое развертывание через Docker

## 🚀 Быстрый запуск с Docker (Рекомендуется)

### Предварительные требования

- Docker
- Docker Compose
- OpenAI API ключ

### 1. Клонирование и настройка

```bash
git clone <your-repo>
cd researcher
```

### 2. Создание конфигурации

Создайте файл `config2.yaml`:

```yaml
llm:
  api_key: "your-openai-api-key-here"
  model: "gpt-4o-mini"
```

### 3. Запуск приложения

```bash
# Простой запуск
./start.sh

# Или вручную
docker-compose up --build -d
```

### 4. Доступ к приложению

- **Streamlit UI**: http://localhost:8502
- **API документация**: http://localhost:8000/docs
- **API endpoint**: http://localhost:8000

### 5. Остановка приложения

```bash
# Простая остановка
./stop.sh

# Или вручную
docker-compose down
```

## 🛠️ Локальная разработка

### Установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Запуск локально

```bash
# Запуск API сервера
python -m uvicorn api:app --reload

# В другом терминале - запуск Streamlit
streamlit run streamlit_app.py
```

## 📝 Использование

### Веб-интерфейс

1. Откройте http://localhost:8502
2. Введите тему исследования
3. Нажмите "Запустить исследование"
4. Дождитесь завершения и скачайте PDF отчет

### API

```python
import requests

# Запуск исследования
response = requests.post("http://localhost:8000/research", 
                        json={"topic": "Искусственный интеллект в 2025"})
topic_id = response.json()["topic_id"]

# Проверка статуса
status = requests.get(f"http://localhost:8000/status/{topic_id}")

# Получение результата
result = requests.get(f"http://localhost:8000/result/{topic_id}")
```

## 🏗️ Архитектура

- **FastAPI** - REST API для асинхронной обработки запросов
- **Streamlit** - веб-интерфейс пользователя
- **OpenAI GPT-4** - языковая модель для анализа и генерации текста
- **WeasyPrint** - генерация PDF документов
- **aiohttp + BeautifulSoup** - асинхронный парсинг веб-страниц
- **Docker** - контейнеризация и развертывание

## 📁 Структура проекта

```
researcher/
├── actions/           # Действия исследования
│   ├── base.py       # Базовый класс действий
│   └── research.py   # Действия исследования
├── roles/            # Роли системы
│   └── researcher.py # Основной класс исследователя
├── utils/            # Утилиты
│   ├── llm.py       # Клиент OpenAI
│   ├── logger.py    # Логирование
│   └── ...
├── Dockerfile        # Docker образ
├── docker-compose.yml # Оркестрация
├── start.sh         # Скрипт запуска
├── stop.sh          # Скрипт остановки
├── api.py           # FastAPI сервер
├── streamlit_app.py # Streamlit интерфейс
└── config2.yaml     # Конфигурация
```

## ⚙️ Конфигурация

### Переменные окружения

- `PYTHONPATH` - путь к Python модулям (автоматически в Docker)

### config2.yaml

```yaml
llm:
  api_key: "your-openai-api-key"  # OpenAI API ключ
  model: "gpt-4o-mini"           # Модель GPT
```

## 🐳 Docker команды

```bash
# Сборка и запуск
docker-compose up --build -d

# Просмотр логов
docker-compose logs api        # Логи API
docker-compose logs streamlit  # Логи Streamlit

# Перезапуск сервисов
docker-compose restart

# Остановка
docker-compose down

# Полная очистка
docker-compose down --rmi all -v --remove-orphans
```

## 🔧 Устранение неполадок

### Docker

1. **Проверьте статус контейнеров**:
   ```bash
   docker-compose ps
   ```

2. **Просмотрите логи**:
   ```bash
   docker-compose logs
   ```

3. **Пересоберите образы**:
   ```bash
   docker-compose up --build --force-recreate
   ```

### API

- API доступно на http://localhost:8000
- Документация: http://localhost:8000/docs
- Проверка здоровья: http://localhost:8000/docs

### Streamlit

- Интерфейс на http://localhost:8502
- Проверьте логи: `docker-compose logs streamlit`

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License 
