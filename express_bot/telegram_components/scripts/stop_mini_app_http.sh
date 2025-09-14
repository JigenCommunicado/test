#!/bin/bash
# Скрипт для остановки Telegram Mini App с HTTP сервером и Cloudflare туннелем

echo "🛑 Остановка Telegram Mini App и всех сервисов..."
echo "==============================================="

cd /root/test/express_bot

# Останавливаем процессы
echo "🔄 Останавливаем процессы..."
pkill -f telegram_bot_mini_app.py
pkill -f telegram_bot_test.py
pkill -f https_server.py
pkill -f "python3 -m http.server"
pkill -f cloudflared

sleep 3

# Восстанавливаем оригинальный файл Mini App
echo "🔄 Восстанавливаем оригинальные файлы..."
if [ -f telegram_mini_app_adaptive.html.bak ]; then
    mv telegram_mini_app_adaptive.html.bak telegram_mini_app_adaptive.html
fi

# Удаляем временные файлы
echo "🧹 Очистка временных файлов..."
rm -f telegram_bot_mini_app.py
rm -f cloudflare.log
rm -f mini_app_server.log

# Проверяем что остановлены
RUNNING_BOTS=$(ps aux | grep -E "(telegram_bot|http.server|cloudflared)" | grep -v grep | wc -l)

if [ "$RUNNING_BOTS" = "0" ]; then
    echo "✅ Все процессы остановлены"
else
    echo "⚠️  Некоторые процессы еще работают:"
    ps aux | grep -E "(telegram_bot|http.server|cloudflared)" | grep -v grep || echo "Нет процессов"
fi

echo "📋 Для запуска: ./start_mini_app_http.sh"
