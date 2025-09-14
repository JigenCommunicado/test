#!/bin/bash
# Скрипт для запуска Telegram Mini App с API прокси

echo "🚀 Запуск Telegram Mini App с API Proxy..."
echo "========================================"

cd /root/test/express_bot

# Остановляем старые процессы
echo "🛑 Останавливаем старые процессы..."
pkill -f telegram_bot_test.py 2>/dev/null
pkill -f telegram_bot_mini_app.py 2>/dev/null
pkill -f api_proxy.py 2>/dev/null
pkill -f "python3 -m http.server" 2>/dev/null
pkill -f cloudflared 2>/dev/null
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

# Запускаем API прокси
echo "🔗 Запускаем API прокси..."
nohup python3 api_proxy.py > api_proxy.log 2>&1 &
PROXY_PID=$!
sleep 3

# Проверяем что прокси запустился
if ! curl -s http://localhost:8445/proxy/health > /dev/null 2>&1; then
    echo "❌ API прокси не запустился. Проверьте логи:"
    cat api_proxy.log
    exit 1
fi
echo "✅ API прокси запущен (PID: $PROXY_PID)"

# Запускаем HTTP сервер для Mini App на порту 8444 
echo "🌐 Запускаем HTTP сервер для Mini App..."
nohup python3 -m http.server 8444 > mini_app_server.log 2>&1 &
HTTP_PID=$!
sleep 3

# Проверяем что HTTP сервер запустился
if ! curl -s http://localhost:8444/telegram_mini_app_adaptive.html > /dev/null 2>&1; then
    echo "❌ HTTP сервер не запустился. Проверьте логи:"
    cat mini_app_server.log
    exit 1
fi
echo "✅ HTTP сервер запущен (PID: $HTTP_PID)"

# Запускаем Cloudflare туннель для API прокси (это даст HTTPS доступ)
echo "🌐 Запускаем Cloudflare туннель для прокси..."
nohup cloudflared tunnel --url http://localhost:8445 > cloudflare_proxy.log 2>&1 &
TUNNEL_PID=$!
sleep 8

# Получаем публичный URL от Cloudflare для прокси
echo "🔍 Получаем публичный URL прокси..."
PROXY_TUNNEL_URL=""
for i in {1..15}; do
    PROXY_TUNNEL_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' cloudflare_proxy.log | head -1)
    if [ ! -z "$PROXY_TUNNEL_URL" ]; then
        break
    fi
    echo "⏳ Ждем Cloudflare туннель для прокси... ($i/15)"
    sleep 2
done

if [ -z "$PROXY_TUNNEL_URL" ]; then
    echo "❌ Не удалось получить URL от Cloudflare для прокси. Проверьте логи:"
    cat cloudflare_proxy.log
    exit 1
fi

echo "✅ Публичный URL прокси получен: $PROXY_TUNNEL_URL"

# Также запускаем туннель для Mini App
echo "🌐 Запускаем Cloudflare туннель для Mini App..."
nohup cloudflared tunnel --url http://localhost:8444 > cloudflare_miniapp.log 2>&1 &
MINIAPP_TUNNEL_PID=$!
sleep 8

# Получаем публичный URL от Cloudflare для Mini App
echo "🔍 Получаем публичный URL Mini App..."
MINIAPP_TUNNEL_URL=""
for i in {1..15}; do
    MINIAPP_TUNNEL_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' cloudflare_miniapp.log | head -1)
    if [ ! -z "$MINIAPP_TUNNEL_URL" ]; then
        break
    fi
    echo "⏳ Ждем Cloudflare туннель для Mini App... ($i/15)"
    sleep 2
done

if [ -z "$MINIAPP_TUNNEL_URL" ]; then
    echo "❌ Не удалось получить URL от Cloudflare для Mini App. Проверьте логи:"
    cat cloudflare_miniapp.log
    exit 1
fi

echo "✅ Публичный URL Mini App получен: $MINIAPP_TUNNEL_URL"

# Создаем временную копию Mini App с правильным URL прокси
echo "📝 Настраиваем Mini App для работы с прокси..."
cp telegram_mini_app_adaptive.html telegram_mini_app_proxy.html
sed -i "s|'/proxy/api/application'|'$PROXY_TUNNEL_URL/proxy/api/application'|g" telegram_mini_app_proxy.html

# Копируем настроенный Mini App на HTTP сервер
cp telegram_mini_app_proxy.html telegram_mini_app_adaptive.html

# Создаем временный файл бота с правильным URL
MINI_APP_URL="$MINIAPP_TUNNEL_URL/telegram_mini_app_adaptive.html"
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

# Тестируем доступность
echo "🧪 Тестируем доступность..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$MINI_APP_URL")
PROXY_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PROXY_TUNNEL_URL/proxy/health")

echo "✅ Mini App: HTTP $HTTP_CODE"
echo "✅ API Proxy: HTTP $PROXY_CODE"

echo ""
echo "🎉 TELEGRAM MINI APP С ПРОКСИ ГОТОВ!"
echo "==================================="
echo "📱 Mini App URL: $MINI_APP_URL"
echo "🔗 API Proxy URL: $PROXY_TUNNEL_URL"
echo "🤖 Telegram Bot: @ExpressSmartAppBot"
echo ""
echo "🔧 Запущенные сервисы:"
echo "• API Proxy: PID $PROXY_PID (порт 8445)"
echo "• HTTP Server: PID $HTTP_PID (порт 8444)"
echo "• Cloudflare Proxy: PID $TUNNEL_PID"
echo "• Cloudflare Mini App: PID $MINIAPP_TUNNEL_PID"
echo "• Bot Process: PID $BOT_PID"
echo ""
echo "📋 ТЕСТИРОВАНИЕ:"
echo "1. Откройте Telegram (мобильное приложение)"
echo "2. Найдите: @ExpressSmartAppBot"
echo "3. Отправьте /start"
echo "4. Нажмите '🚀 Mini App'"
echo "5. Заполните и отправьте заявку"
echo ""
echo "🔧 Теперь должно работать как в десктопе, так и в мобильном!"
echo "📝 Для остановки: ./stop_mini_app_with_proxy.sh"
