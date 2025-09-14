#!/bin/bash
# Скрипт для остановки Telegram Mini App с Cloudflare туннелем

echo "🛑 Остановка Telegram Mini App и Cloudflare туннеля..."
echo "===================================================="

cd /root/test/express_bot

# Останавливаем процессы
echo "🔄 Останавливаем процессы..."
pkill -f telegram_bot_mini_app.py
pkill -f telegram_bot_test.py
pkill -f https_server.py
pkill -f cloudflared

sleep 3

# Удаляем временные файлы
echo "🧹 Очистка временных файлов..."
rm -f telegram_bot_mini_app.py
rm -f cloudflare.log

# Проверяем что остановлены
RUNNING_BOTS=$(ps aux | grep -E "(telegram_bot|https_server|cloudflared)" | grep -v grep | wc -l)

if [ "$RUNNING_BOTS" = "0" ]; then
    echo "✅ Все процессы остановлены"
else
    echo "⚠️  Некоторые процессы еще работают:"
    ps aux | grep -E "(telegram_bot|https_server|cloudflared)" | grep -v grep || echo "Нет процессов"
fi

echo "📋 Для запуска: ./start_mini_app_cloudflare.sh"
