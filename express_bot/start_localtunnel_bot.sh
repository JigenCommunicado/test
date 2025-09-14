#!/bin/bash

echo "🚀 Запуск Express Bot с LocalTunnel..."

# Останавливаем предыдущие процессы
echo "🛑 Останавливаем предыдущие процессы..."
pkill -f express_bot_with_admin
pkill -f localtunnel
sleep 2

# Запускаем бот на порту 5011
echo "🤖 Запускаем бот на порту 5011..."
cd /root/test/express_bot
python3 express_bot_localtunnel.py &
BOT_PID=$!
echo "✅ Бот запущен (PID: $BOT_PID)"

# Ждем запуска бота
echo "⏳ Ждем запуска бота..."
sleep 5

# Запускаем LocalTunnel на порт 5011
echo "🌐 Запускаем LocalTunnel на порт 5011..."
npx localtunnel --port 5011 --subdomain express-bot-flight &
TUNNEL_PID=$!
echo "✅ LocalTunnel запущен (PID: $TUNNEL_PID)"

# Ждем запуска туннеля
echo "⏳ Ждем запуска туннеля..."
sleep 8

# Проверяем статус
echo "📊 Проверяем статус..."
ps aux | grep -E "(express_bot_localtunnel|localtunnel)" | grep -v grep

echo ""
echo "🎉 Готово!"
echo "📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99"
echo "🌐 Webhook URL: https://express-bot-flight.loca.lt/webhook"
echo "👨‍💼 Admin Panel: https://express-bot-flight.loca.lt/admin"
echo "🔧 Local Server: http://localhost:5011"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте админ панель Express.ms"
echo "2. Добавьте бота как SmartApp"
echo "3. Укажите webhook URL: https://express-bot-flight.loca.lt/webhook"
echo "4. Протестируйте команду /start"
echo ""
echo "🔧 Для остановки: pkill -f express_bot_localtunnel && pkill -f localtunnel"
echo ""
echo "🧪 Тестирование:"
echo "curl https://express-bot-flight.loca.lt/health"
echo "curl https://express-bot-flight.loca.lt/manifest"

