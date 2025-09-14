#!/bin/bash
# Скрипт для остановки финального Telegram Mini App

echo "🛑 Остановка финального Telegram Mini App..."
echo "=========================================="

cd /root/test/express_bot

# Останавливаем процессы
echo "🔄 Останавливаем процессы..."
pkill -f telegram_bot_mini_app.py
pkill -f telegram_bot_test.py
pkill -f "python3 -m http.server"
pkill -f cloudflared

sleep 3

# Восстанавливаем оригинальные файлы
echo "🔄 Восстанавливаем оригинальные файлы..."
if [ -f telegram_mini_app_adaptive.html.bak ]; then
    cp telegram_mini_app_adaptive.html.bak telegram_mini_app_adaptive.html
fi

# Удаляем временные файлы
echo "🧹 Очистка временных файлов..."
rm -f telegram_bot_mini_app.py
rm -f cloudflare.log
rm -f mini_app_server.log

# Проверяем что остановлены
RUNNING_PROCESSES=$(ps aux | grep -E "(telegram_bot|http.server|cloudflared)" | grep -v grep | wc -l)

if [ "$RUNNING_PROCESSES" = "0" ]; then
    echo "✅ Все процессы остановлены"
else
    echo "⚠️  Некоторые процессы еще работают:"
    ps aux | grep -E "(telegram_bot|http.server|cloudflared)" | grep -v grep || echo "Нет процессов"
fi

echo "📋 Для запуска: ./start_final_mini_app.sh"
