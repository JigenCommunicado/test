#!/bin/bash

echo "🚀 Запуск Express.ms Bot Docker"
echo "==============================="

# Проверка, что мы в правильной директории
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Файл docker-compose.yml не найден. Запустите из директории с ботом."
    exit 1
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден. Скопируйте env.example в .env и настройте."
    exit 1
fi

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Сборка и запуск
echo "🔨 Сборка и запуск бота..."
docker-compose up --build -d

# Ожидание запуска
echo "⏳ Ожидание запуска бота..."
sleep 15

# Проверка статуса
echo "🔍 Проверка статуса..."
docker-compose ps

# Проверка health
echo "🏥 Проверка health check..."
sleep 5
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "❌ Health check не прошел"

echo ""
echo "✅ Бот запущен!"
echo "🌐 Доступные endpoints:"
echo "   - Health: http://localhost:8000/health"
echo "   - Manifest: http://localhost:8000/manifest"
echo "   - Stats: http://localhost:8000/stats"
echo "   - Webhook: http://localhost:8000/webhook"
echo ""
echo "📋 Логи: docker-compose logs -f"
echo "🛑 Остановка: docker-compose down"
