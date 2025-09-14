#!/bin/bash
# Скрипт для остановки Telegram Mini App

echo "🛑 Остановка Telegram Mini App..."
echo "================================="

cd /root/test/express_bot

# Останавливаем процессы
echo "🔄 Останавливаем процессы..."
pkill -f telegram_bot_test.py
pkill -f https_server.py

sleep 2

# Проверяем что остановлены
RUNNING_BOTS=$(ps aux | grep -c "telegram_bot_test.py" | grep -v grep || echo "0")
RUNNING_HTTPS=$(ps aux | grep -c "https_server.py" | grep -v grep || echo "0")

if [ "$RUNNING_BOTS" = "0" ] && [ "$RUNNING_HTTPS" = "0" ]; then
    echo "✅ Все процессы остановлены"
else
    echo "⚠️  Некоторые процессы еще работают:"
    ps aux | grep -E "(telegram_bot_test|https_server)" | grep -v grep || echo "Нет процессов"
fi

echo "📋 Для запуска: ./start_mini_app.sh"
