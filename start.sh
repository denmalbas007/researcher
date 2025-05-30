#!/bin/bash

echo "🚀 Запуск AI Researcher приложения..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose."
    exit 1
fi

# Проверяем наличие config2.yaml
if [ ! -f "config2.yaml" ]; then
    echo "❌ Файл config2.yaml не найден. Создайте его с вашими настройками OpenAI API."
    echo "Пример содержимого:"
    echo "llm:"
    echo "  api_key: 'your-openai-api-key'"
    echo "  model: 'gpt-4o-mini'"
    exit 1
fi

# Создаем директорию для отчетов если её нет
mkdir -p research_reports

echo "📦 Сборка и запуск контейнеров..."
docker-compose up --build -d

echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверяем статус сервисов
echo "📊 Проверка статуса сервисов:"
docker-compose ps

echo ""
echo "✅ Приложение запущено!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   - Streamlit UI: http://localhost:8502"
echo "   - FastAPI Docs: http://localhost:8000/docs"
echo "   - API endpoint: http://localhost:8000"
echo ""
echo "📝 Команды управления:"
echo "   - Остановить: docker-compose down"
echo "   - Логи API: docker-compose logs api"
echo "   - Логи Streamlit: docker-compose logs streamlit"
echo "   - Перезапустить: docker-compose restart"
echo "" 