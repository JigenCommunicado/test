#!/bin/bash

# Скрипт для запуска всех серверов Express SmartApp
# Автор: AI Assistant
# Дата: $(date)

echo "🚀 Запуск Express SmartApp серверов..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Останавливаем все существующие процессы
echo "🛑 Остановка существующих процессов..."
pkill -f smartapp_flight_booking.py
pkill -f "http.server"
sleep 2

# Активируем виртуальное окружение и запускаем Flask сервер
echo "🐍 Запуск Flask API сервера (порт 5002)..."
source venv/bin/activate
nohup python3 smartapp_flight_booking.py > smartapp.log 2>&1 &
FLASK_PID=$!

# Ждем запуска Flask сервера
sleep 3

# Запускаем статический сервер
echo "📁 Запуск статического сервера (порт 8080)..."
nohup python3 -m http.server 8080 > static.log 2>&1 &
STATIC_PID=$!

# Ждем запуска статического сервера
sleep 2

# Проверяем статус серверов
echo "🔍 Проверка статуса серверов..."

# Проверяем Flask сервер
if curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "✅ Flask API сервер запущен (порт 5002)"
else
    echo "❌ Flask API сервер не отвечает"
fi

# Проверяем статический сервер
if curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "✅ Статический сервер запущен (порт 8080)"
else
    echo "❌ Статический сервер не отвечает"
fi

# Сохраняем PID процессов
echo $FLASK_PID > flask.pid
echo $STATIC_PID > static.pid

echo ""
echo "🎉 Все серверы запущены!"
echo ""
echo "📱 Доступные ссылки:"
echo "   • Главная навигация: http://localhost:8080/index.html"
echo "   • Форма заявки (ПК): http://localhost:8080/flight_booking_ui.html"
echo "   • Форма заявки (мобильная): http://localhost:8080/mobile_booking_ui.html"
echo "   • Админ панель: http://localhost:8080/admin_panel.html"
echo "   • Управление периодами: http://localhost:8080/application_periods.html"
echo "   • Поиск заявок: http://localhost:8080/search_interface.html"
echo "   • Уведомления: http://localhost:8080/notifications.html"
echo ""
echo "📊 API endpoints:"
echo "   • Health Check: http://localhost:5002/health"
echo "   • Статистика: http://localhost:5002/api/statistics"
echo ""
echo "📝 Логи:"
echo "   • Flask сервер: tail -f smartapp.log"
echo "   • Статический сервер: tail -f static.log"
echo ""
echo "🛑 Для остановки серверов выполните: ./stop_servers.sh"

