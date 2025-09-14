#!/bin/bash
"""
Скрипт для запуска исправленного Express бота
"""

echo "🚀 Запуск исправленного Express Bot..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Останавливаем старые процессы
echo "🛑 Останавливаем старые процессы..."
pkill -f "express_bot.py" 2>/dev/null || true
pkill -f "express_bot_webhook.py" 2>/dev/null || true
pkill -f "express_smartapp_proper.py" 2>/dev/null || true

# Ждем завершения процессов
sleep 2

# Проверяем, что порты свободны
echo "🔍 Проверяем порты..."
if lsof -Pi :5007 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Порт 5007 занят, освобождаем..."
    kill -9 $(lsof -Pi :5007 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 1
fi

# Запускаем настройку бота
echo "⚙️ Настраиваем бота..."
python3 setup_express_bot.py

# Запускаем исправленный бот
echo "🤖 Запускаем исправленный бот..."
nohup python3 express_bot_fixed.py > fixed_bot.log 2>&1 &
BOT_PID=$!

# Ждем запуска
sleep 3

# Проверяем статус
echo "📊 Проверяем статус бота..."
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Бот запущен успешно (PID: $BOT_PID)"
    echo "📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99"
    echo "🌐 Webhook URL: https://comparing-doom-solving-royalty.trycloudflare.com/webhook"
    echo "🔗 Health Check: http://localhost:5007/health"
    echo "📋 Manifest: http://localhost:5007/manifest"
    echo ""
    echo "📝 Логи: tail -f fixed_bot.log"
    echo "🛑 Остановка: kill $BOT_PID"
else
    echo "❌ Ошибка запуска бота"
    echo "📝 Проверьте логи: cat fixed_bot.log"
    exit 1
fi

# Тестируем подключение
echo "🧪 Тестируем подключение..."
curl -s http://localhost:5007/health | jq . 2>/dev/null || echo "❌ Health check не прошел"

echo ""
echo "🎉 Готово! Бот должен быть онлайн в Express.ms"
echo "📋 Следующие шаги:"
echo "1. Проверьте статус бота в Express.ms"
echo "2. Протестируйте команду /start"
echo "3. Проверьте логи: tail -f fixed_bot.log"


