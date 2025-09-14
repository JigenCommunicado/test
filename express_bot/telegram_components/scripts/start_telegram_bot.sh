#!/bin/bash

# Скрипт запуска Telegram бота для системы подачи заявок

echo "🤖 Запуск Telegram бота..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте его командой: python3 -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем наличие токена бота
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  Токен Telegram бота не установлен!"
    echo ""
    echo "📋 Инструкция по настройке:"
    echo "1. Создайте бота через @BotFather в Telegram"
    echo "2. Получите токен"
    echo "3. Установите переменную окружения:"
    echo "   export TELEGRAM_BOT_TOKEN='ваш_токен_здесь'"
    echo ""
    echo "Или создайте файл .env с токеном:"
    echo "   echo 'TELEGRAM_BOT_TOKEN=ваш_токен_здесь' > .env"
    echo ""
    echo "📖 Подробная инструкция: cat TELEGRAM_SETUP.md"
    exit 1
fi

# Проверяем доступность Flask API
echo "🔍 Проверяем доступность Flask API..."
if ! curl -s http://localhost:5002/health > /dev/null; then
    echo "❌ Flask API сервер недоступен на порту 5002!"
    echo "Запустите его командой: python3 smartapp_flight_booking.py"
    echo "Или используйте: ./start_servers.sh"
    exit 1
fi

# Проверяем доступность статического сервера
echo "🔍 Проверяем доступность статического сервера..."
if ! curl -s http://localhost:8080/ > /dev/null; then
    echo "⚠️  Статический сервер недоступен на порту 8080!"
    echo "Рекомендуется запустить его командой: python3 -m http.server 8080"
    echo "Или используйте: ./start_servers.sh"
    echo ""
    echo "Mini App может работать некорректно без статического сервера."
    read -p "Продолжить запуск бота? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Проверяем наличие зависимостей
echo "📦 Проверяем зависимости..."
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "❌ Зависимость python-telegram-bot не установлена!"
    echo "Установите командой: pip install python-telegram-bot==20.7"
    exit 1
fi

if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo "❌ Зависимость aiohttp не установлена!"
    echo "Установите командой: pip install aiohttp==3.9.1"
    exit 1
fi

echo "✅ Все проверки пройдены!"
echo ""
echo "🚀 Запускаем Telegram бота..."
echo "📱 Mini App URL: http://localhost:8080/telegram_mini_app.html"
echo "🔗 API URL: http://localhost:5002"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo "==============================================="

# Запускаем бота
python3 telegram_bot.py
