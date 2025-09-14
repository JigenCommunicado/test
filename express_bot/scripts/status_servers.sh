#!/bin/bash

# Скрипт для проверки статуса серверов Express SmartApp
# Автор: AI Assistant
# Дата: $(date)

echo "🔍 Проверка статуса Express SmartApp серверов..."
echo ""

# Переходим в директорию проекта
cd /root/test/express_bot

# Проверяем Flask сервер
echo "🐍 Flask API сервер (порт 5002):"
if curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "   ✅ Статус: Запущен"
    echo "   📊 Health Check: $(curl -s http://localhost:5002/health | head -1)"
else
    echo "   ❌ Статус: Не запущен"
fi

# Проверяем статический сервер
echo ""
echo "📁 Статический сервер (порт 8080):"
if curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "   ✅ Статус: Запущен"
    echo "   📊 Главная страница: Доступна"
else
    echo "   ❌ Статус: Не запущен"
fi

# Проверяем процессы
echo ""
echo "🔍 Активные процессы:"
echo "   Flask сервер:"
if pgrep -f smartapp_flight_booking.py > /dev/null; then
    echo "   ✅ Процесс найден (PID: $(pgrep -f smartapp_flight_booking.py))"
else
    echo "   ❌ Процесс не найден"
fi

echo "   Статический сервер:"
if pgrep -f "http.server" > /dev/null; then
    echo "   ✅ Процесс найден (PID: $(pgrep -f "http.server"))"
else
    echo "   ❌ Процесс не найден"
fi

# Проверяем порты
echo ""
echo "🔍 Использование портов:"
echo "   Порт 5002:"
if lsof -i :5002 > /dev/null 2>&1; then
    echo "   ✅ Занят"
else
    echo "   ❌ Свободен"
fi

echo "   Порт 8080:"
if lsof -i :8080 > /dev/null 2>&1; then
    echo "   ✅ Занят"
else
    echo "   ❌ Свободен"
fi

# Показываем последние логи
echo ""
echo "📝 Последние логи Flask сервера:"
if [ -f smartapp.log ]; then
    echo "   $(tail -3 smartapp.log | sed 's/^/   /')"
else
    echo "   ❌ Лог файл не найден"
fi

echo ""
echo "📝 Последние логи статического сервера:"
if [ -f static.log ]; then
    echo "   $(tail -3 static.log | sed 's/^/   /')"
else
    echo "   ❌ Лог файл не найден"
fi

echo ""
echo "🎯 Доступные команды:"
echo "   • Запуск: ./start_servers.sh"
echo "   • Остановка: ./stop_servers.sh"
echo "   • Перезапуск: ./restart_servers.sh"
echo "   • Статус: ./status_servers.sh"

