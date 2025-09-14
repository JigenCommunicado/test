#!/bin/bash
# Скрипт для запуска Telegram Mini App с публичным HTTPS через ngrok

echo "🚀 Запуск Telegram Mini App с публичным доступом..."
echo "=================================================="

cd /root/test/express_bot

# Остановляем старые процессы
echo "🛑 Останавливаем старые процессы..."
pkill -f telegram_bot_test.py 2>/dev/null
pkill -f https_server.py 2>/dev/null
pkill -f ngrok 2>/dev/null
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
if ! curl -k -s https://localhost:8443/telegram_mini_app_adaptive.html > /dev/null 2>&1; then
    echo "❌ HTTPS сервер не запустился. Проверьте логи:"
    cat https_server.log
    exit 1
fi
echo "✅ HTTPS сервер запущен (PID: $HTTPS_PID)"

# Запускаем ngrok для создания публичного HTTPS URL
echo "🌐 Запускаем ngrok туннель..."
nohup ngrok http 8443 > ngrok.log 2>&1 &
NGROK_PID=$!
sleep 5

# Получаем публичный URL от ngrok
echo "🔍 Получаем публичный URL..."
NGROK_URL=""
for i in {1..10}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1)
    if [ ! -z "$NGROK_URL" ]; then
        break
    fi
    echo "⏳ Ждем ngrok... ($i/10)"
    sleep 2
done

if [ -z "$NGROK_URL" ]; then
    echo "❌ Не удалось получить URL от ngrok. Проверьте логи:"
    cat ngrok.log
    exit 1
fi

echo "✅ Публичный URL получен: $NGROK_URL"

# Создаем временный файл бота с правильным URL
MINI_APP_URL="$NGROK_URL/telegram_mini_app_adaptive.html"
echo "📝 Обновляем URL в боте: $MINI_APP_URL"

# Создаем временную копию бота с правильным URL
cp telegram_bot_test.py telegram_bot_mini_app.py
sed -i "s|https://localhost:8443/telegram_mini_app.html|$MINI_APP_URL|g" telegram_bot_mini_app.py

# Добавляем кнопку Mini App обратно
sed -i 's|InlineKeyboardButton("🌐 Ссылки", callback_data="links"),|InlineKeyboardButton("🚀 Mini App", web_app=WebAppInfo(url="'$MINI_APP_URL'")),|g' telegram_bot_mini_app.py

# Запускаем обновленного Telegram бота
echo "🤖 Запускаем Telegram бота с Mini App..."
export TELEGRAM_BOT_TOKEN="8068288968:AAFXyi2e8rHRWHxaWUx0mzU3HDkB7rmZ63c"
nohup bash -c "source venv/bin/activate && python3 telegram_bot_mini_app.py" > telegram_bot_mini.log 2>&1 &
BOT_PID=$!
sleep 3

# Проверяем что бот запустился
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Telegram бот запущен (PID: $BOT_PID)"
else
    echo "❌ Telegram бот не запустился. Проверьте логи:"
    tail -10 telegram_bot_mini.log
    exit 1
fi

echo ""
echo "🎉 TELEGRAM MINI APP ГОТОВ К ТЕСТИРОВАНИЮ!"
echo "=========================================="
echo "📱 Mini App URL: $MINI_APP_URL"
echo "🤖 Telegram Bot: @ExpressSmartAppBot"
echo "🌐 ngrok URL: $NGROK_URL"
echo "🔐 HTTPS Server: PID $HTTPS_PID"
echo "🌐 ngrok Process: PID $NGROK_PID"
echo "🤖 Bot Process: PID $BOT_PID"
echo ""
echo "📋 Найдите бота в Telegram и нажмите кнопку '🚀 Mini App'"
echo "📝 Для остановки: ./stop_mini_app_public.sh"
echo ""
echo "📊 Проверить статус ngrok: curl http://localhost:4040/api/tunnels"
echo "📋 Логи ngrok: cat ngrok.log"
