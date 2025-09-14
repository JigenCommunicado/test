#!/bin/bash
# Скрипт остановки правильного Express SmartApp

echo "🛑 Остановка Express SmartApp (правильная версия)..."
echo "=================================================="

cd /root/test/express_bot

# Останавливаем Express SmartApp
echo "🔄 Останавливаем Express SmartApp..."
pkill -f express_smartapp_proper.py
sleep 2

# Проверяем что остановлен
RUNNING_PROCESSES=$(ps aux | grep express_smartapp_proper | grep -v grep | wc -l)

if [ "$RUNNING_PROCESSES" = "0" ]; then
    echo "✅ Express SmartApp остановлен"
else
    echo "⚠️  Некоторые процессы еще работают:"
    ps aux | grep express_smartapp_proper | grep -v grep || echo "Нет процессов"
fi

echo "📋 Для запуска: ./start_express_smartapp_proper.sh"







