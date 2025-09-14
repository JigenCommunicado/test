#!/bin/bash

echo "🛑 Остановка Express Bot с CloudPub..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Проверяем, есть ли файл с PID
if [ -f "cloudpub_bot.pid" ]; then
    BOT_PID=$(cat cloudpub_bot.pid)
    echo "📱 Останавливаем процесс с PID: $BOT_PID"
    
    if ps -p $BOT_PID > /dev/null; then
        kill $BOT_PID
        echo "✅ Процесс остановлен"
    else
        echo "⚠️ Процесс уже не запущен"
    fi
    
    rm cloudpub_bot.pid
else
    echo "⚠️ Файл PID не найден, ищем процесс вручную..."
    pkill -f "express_bot_cloudpub.py"
    echo "✅ Процесс остановлен"
fi

# Проверяем, что порт 5011 свободен
if lsof -Pi :5011 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Порт 5011 все еще занят, принудительно освобождаем..."
    fuser -k 5011/tcp
    sleep 2
fi

echo "✅ Express Bot остановлен"
echo "🌐 CloudPub туннель продолжает работать"
echo "📋 Для полной остановки CloudPub выполните: sudo clo stop express-bot"
