#!/bin/bash
# Скрипт для запуска Telegram Mini App с публичным HTTPS через Cloudflare Tunnel

echo "🚀 Запуск Telegram Mini App с Cloudflare Tunnel..."
echo "==============================================="

cd /root/test/express_bot

# Остановляем старые процессы
echo "🛑 Останавливаем старые процессы..."
pkill -f telegram_bot_test.py 2>/dev/null
pkill -f telegram_bot_mini_app.py 2>/dev/null
pkill -f https_server.py 2>/dev/null
pkill -f cloudflared 2>/dev/null
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

# Запускаем Cloudflare туннель для создания публичного HTTPS URL
echo "🌐 Запускаем Cloudflare туннель..."
nohup cloudflared tunnel --url https://localhost:8443 > cloudflare.log 2>&1 &
TUNNEL_PID=$!
sleep 8

# Получаем публичный URL от Cloudflare
echo "🔍 Получаем публичный URL..."
TUNNEL_URL=""
for i in {1..15}; do
    TUNNEL_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' cloudflare.log | head -1)
    if [ ! -z "$TUNNEL_URL" ]; then
        break
    fi
    echo "⏳ Ждем Cloudflare туннель... ($i/15)"
    sleep 2
done

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Не удалось получить URL от Cloudflare. Проверьте логи:"
    cat cloudflare.log
    exit 1
fi

echo "✅ Публичный URL получен: $TUNNEL_URL"

# Создаем временный файл бота с правильным URL
MINI_APP_URL="$TUNNEL_URL/telegram_mini_app_adaptive.html"
echo "📝 Обновляем URL в боте: $MINI_APP_URL"

# Создаем временную копию бота с правильным URL
cp telegram_bot_test.py telegram_bot_mini_app.py

# Заменяем кнопку "🌐 Ссылки" на "🚀 Mini App" с правильным URL
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

# Тестируем доступность Mini App
echo "🧪 Тестируем доступность Mini App..."
if curl -s "$MINI_APP_URL" > /dev/null 2>&1; then
    echo "✅ Mini App доступен по публичному URL"
else
    echo "⚠️  Mini App может быть недоступен. Проверьте URL вручную."
fi

echo ""
echo "🎉 TELEGRAM MINI APP ГОТОВ К ТЕСТИРОВАНИЮ!"
echo "=========================================="
echo "📱 Mini App URL: $MINI_APP_URL"
echo "🤖 Telegram Bot: @ExpressSmartAppBot"
echo "🌐 Cloudflare URL: $TUNNEL_URL" 
echo "🔐 HTTPS Server: PID $HTTPS_PID"
echo "🌐 Cloudflare Tunnel: PID $TUNNEL_PID"
echo "🤖 Bot Process: PID $BOT_PID"
echo ""
echo "📋 ИНСТРУКЦИЯ ПО ТЕСТИРОВАНИЮ:"
echo "1. Откройте Telegram (мобильное приложение рекомендуется)"
echo "2. Найдите бота: @ExpressSmartAppBot"
echo "3. Отправьте /start"
echo "4. Нажмите кнопку '🚀 Mini App'"
echo "5. Заполните форму заявки"
echo ""
echo "🔧 Особенности адаптивного интерфейса:"
echo "• 💻 В веб-версии Telegram: компактный ПК интерфейс"
echo "• 📱 В мобильном Telegram: оптимизированный мобильный интерфейс"
echo "• 🎨 Автоматическое применение темы Telegram"
echo "• 👤 Автозаполнение ФИО из профиля Telegram"
echo ""
echo "📝 Для остановки: ./stop_mini_app_cloudflare.sh"
echo "📋 Логи Cloudflare: cat cloudflare.log"
