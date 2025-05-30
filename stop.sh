#!/bin/bash

echo "🛑 Остановка AI Researcher приложения..."

# Останавливаем контейнеры
docker-compose down

echo "🧹 Очистка (опционально):"
echo "   - Удалить образы: docker-compose down --rmi all"
echo "   - Удалить volumes: docker-compose down -v"
echo "   - Полная очистка: docker-compose down --rmi all -v --remove-orphans"

echo "✅ Приложение остановлено!" 