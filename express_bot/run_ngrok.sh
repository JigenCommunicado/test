#!/bin/bash

# Простой скрипт запуска ngrok для Express Bot

echo "🐳 Запуск Express Bot с ngrok..."

# Устанавливаем переменные окружения
export POSTGRES_PASSWORD=express_bot_password
export POSTGRES_DB=express_bot_db
export POSTGRES_USER=express_bot_user
export BOT_CREDENTIALS=00c46d64-1127-5a96-812d-3d8b27c58b99:a75b4cd97d9e88e543f077178b2d5a4f
export HOST=https://api.express.ms
export DATABASE_URL=postgresql://express_bot_user:express_bot_password@postgres:5432/express_bot_db
export REDIS_URL=redis://redis:6379/0
export LOG_LEVEL=INFO

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose -f docker-compose.ngrok.yml down

# Запускаем сервисы
echo "🚀 Запускаем Docker сервисы..."
docker-compose -f docker-compose.ngrok.yml up -d

# Ждем запуска
echo "⏳ Ожидаем запуска сервисов..."
sleep 15

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose -f docker-compose.ngrok.yml ps

echo ""
echo "🎉 Express Bot с ngrok запущен!"
echo ""
echo "🌐 Веб-интерфейсы:"
echo "  ngrok: http://localhost:4040"
echo "  Bot health: http://localhost:8000/health"
echo ""
echo "📋 Полезные команды:"
echo "  Просмотр логов: docker-compose -f docker-compose.ngrok.yml logs -f"
echo "  Остановка: docker-compose -f docker-compose.ngrok.yml down"
