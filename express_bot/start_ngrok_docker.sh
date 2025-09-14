#!/bin/bash

# Скрипт запуска Express Bot с ngrok в Docker

echo "🐳 Запуск Express Bot с ngrok в Docker..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Переходим в директорию проекта
cd /root/test/express_bot

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл..."
    cat > .env << EOF
# Express Bot Environment Variables
BOT_CREDENTIALS=00c46d64-1127-5a96-812d-3d8b27c58b99:a75b4cd97d9e88e543f077178b2d5a4f
HOST=https://api.express.ms
DATABASE_URL=postgresql://express_bot_user:express_bot_password@postgres:5432/express_bot_db
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=INFO
NGROK_URL=
EOF
    echo "✅ .env файл создан"
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose -f docker-compose.ngrok.yml down

# Запускаем сервисы
echo "🚀 Запускаем Docker сервисы..."
docker-compose -f docker-compose.ngrok.yml up -d

# Ждем запуска
echo "⏳ Ожидаем запуска сервисов..."
sleep 10

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose -f docker-compose.ngrok.yml ps

# Получаем URL ngrok
echo "🌐 Получаем URL ngrok..."
sleep 5

# Пытаемся получить URL через API ngrok
NGROK_URL=""
for i in {1..10}; do
    if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('tunnels'):
        print(data['tunnels'][0]['public_url'])
except:
    pass
" 2>/dev/null)
        break
    fi
    sleep 2
done

if [ -n "$NGROK_URL" ]; then
    echo "✅ ngrok туннель: $NGROK_URL"
    echo "🌐 Webhook URL: $NGROK_URL/webhook"
    echo "📊 ngrok веб-интерфейс: http://localhost:4040"
    
    # Обновляем .env файл
    sed -i "s/NGROK_URL=.*/NGROK_URL=$NGROK_URL/" .env
    echo "✅ .env файл обновлен"
else
    echo "⚠️ Не удалось получить URL ngrok"
    echo "Проверьте логи: docker-compose -f docker-compose.ngrok.yml logs ngrok"
fi

echo ""
echo "🎉 Express Bot с ngrok запущен!"
echo ""
echo "📋 Полезные команды:"
echo "  Просмотр логов: docker-compose -f docker-compose.ngrok.yml logs -f"
echo "  Остановка: docker-compose -f docker-compose.ngrok.yml down"
echo "  Перезапуск: docker-compose -f docker-compose.ngrok.yml restart"
echo ""
echo "🌐 Веб-интерфейсы:"
echo "  ngrok: http://localhost:4040"
echo "  Bot health: http://localhost:8000/health"
if [ -n "$NGROK_URL" ]; then
    echo "  Bot webhook: $NGROK_URL/webhook"
fi
