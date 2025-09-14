#!/bin/bash

# Скрипт для остановки всех серверов Express SmartApp
# Автор: AI Assistant
# Дата: $(date)

echo "🛑 Остановка Express SmartApp серверов..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Останавливаем Flask сервер
echo "🐍 Остановка Flask API сервера..."
if [ -f flask.pid ]; then
    FLASK_PID=$(cat flask.pid)
    if kill -0 $FLASK_PID 2>/dev/null; then
        kill $FLASK_PID
        echo "✅ Flask сервер остановлен (PID: $FLASK_PID)"
    else
        echo "⚠️  Flask сервер уже остановлен"
    fi
    rm -f flask.pid
else
    echo "⚠️  PID файл Flask сервера не найден"
fi

# Останавливаем статический сервер
echo "📁 Остановка статического сервера..."
if [ -f static.pid ]; then
    STATIC_PID=$(cat static.pid)
    if kill -0 $STATIC_PID 2>/dev/null; then
        kill $STATIC_PID
        echo "✅ Статический сервер остановлен (PID: $STATIC_PID)"
    else
        echo "⚠️  Статический сервер уже остановлен"
    fi
    rm -f static.pid
else
    echo "⚠️  PID файл статического сервера не найден"
fi

# Принудительно останавливаем все процессы
echo "🔍 Поиск и остановка оставшихся процессов..."
pkill -f smartapp_flight_booking.py
pkill -f "http.server"

# Ждем завершения процессов
sleep 2

# Проверяем, что порты свободны
echo "🔍 Проверка освобождения портов..."

if ! lsof -i :5002 > /dev/null 2>&1; then
    echo "✅ Порт 5002 освобожден"
else
    echo "❌ Порт 5002 все еще занят"
fi

if ! lsof -i :8080 > /dev/null 2>&1; then
    echo "✅ Порт 8080 освобожден"
else
    echo "❌ Порт 8080 все еще занят"
fi

echo ""
echo "🎉 Все серверы остановлены!"
echo ""
echo "📝 Для запуска серверов выполните: ./start_servers.sh"

