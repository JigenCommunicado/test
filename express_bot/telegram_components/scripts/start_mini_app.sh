#!/bin/bash
# Скрипт для запуска Telegram Mini App с HTTPS

echo "🚀 Запуск Telegram Mini App..."
echo "================================"

cd /root/test/express_bot

# Проверяем наличие сертификатов
if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
    echo "🔐 Создаем SSL сертификаты..."
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
        -subj "/C=RU/ST=Moscow/L=Moscow/O=ExpressSmartApp/CN=localhost"
    echo "✅ SSL сертификаты созданы"
fi

# Останавливаем старые процессы
echo "🛑 Останавливаем старые процессы..."
pkill -f telegram_bot_test.py 2>/dev/null
pkill -f https_server.py 2>/dev/null
sleep 2

# Проверяем Flask API
echo "🔍 Проверяем Flask API..."
if ! curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "❌ Flask API недоступен. Запустите сначала ./start_servers.sh"
    exit 1
fi
echo "✅ Flask API работает"

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем HTTPS сервер в фоне
echo "🔐 Запускаем HTTPS сервер..."
nohup python3 https_server.py > https_server.log 2>&1 &
HTTPS_PID=$!
sleep 3

# Проверяем что HTTPS сервер запустился
if curl -k -s https://localhost:8443/telegram_mini_app.html > /dev/null 2>&1; then
    echo "✅ HTTPS сервер запущен (PID: $HTTPS_PID)"
else
    echo "❌ HTTPS сервер не запустился. Проверьте логи:"
    cat https_server.log
    exit 1
fi

# Запускаем Telegram бота
echo "🤖 Запускаем Telegram бота..."
export TELEGRAM_BOT_TOKEN="8068288968:AAFXyi2e8rHRWHxaWUx0mzU3HDkB7rmZ63c"
nohup bash -c "source venv/bin/activate && python3 telegram_bot_test.py" > telegram_bot.log 2>&1 &
BOT_PID=$!
sleep 3

# Проверяем что бот запустился
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Telegram бот запущен (PID: $BOT_PID)"
else
    echo "❌ Telegram бот не запустился. Проверьте логи:"
    tail -10 telegram_bot.log
    exit 1
fi

echo ""
echo "🎉 ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!"
echo "========================"
echo "📱 Mini App URL: https://localhost:8443/telegram_mini_app.html"
echo "🤖 Telegram Bot: @ExpressSmartAppBot"
echo "🔐 HTTPS Server: PID $HTTPS_PID"
echo "🤖 Bot Process: PID $BOT_PID"
echo ""
echo "📋 Найдите бота в Telegram и нажмите кнопку '🚀 Mini App'"
echo "📝 Для остановки: ./stop_mini_app.sh"
