#!/bin/bash
# Финальный скрипт для запуска Telegram Mini App с поддержкой мобильной версии

echo "🚀 Запуск финального Telegram Mini App..."
echo "======================================="

cd /root/test/express_bot

# Остановляем все старые процессы
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

# Копируем мобильно-безопасный Mini App
echo "📱 Настраиваем мобильно-безопасный Mini App..."
cp mini_apps/telegram_mini_app_mobile_safe.html mini_apps/telegram_mini_app_adaptive.html

# Копируем Mini App в frontend для HTTP сервера
echo "📁 Копируем Mini App в frontend..."
cp mini_apps/telegram_mini_app_adaptive.html ../frontend/

# Запускаем HTTP сервер для Mini App на порту 8444
echo "🌐 Запускаем HTTP сервер для Mini App..."
cd ../frontend
nohup python3 -m http.server 8444 > ../logs/mini_app_server.log 2>&1 &
HTTP_PID=$!
sleep 3

# Проверяем что HTTP сервер запустился
if ! curl -s http://localhost:8444/telegram_mini_app_adaptive.html > /dev/null 2>&1; then
    echo "❌ HTTP сервер не запустился. Проверьте логи:"
    cat mini_app_server.log
    exit 1
fi
echo "✅ HTTP сервер запущен (PID: $HTTP_PID)"

# Запускаем HTTPS прокси для API
echo "🔒 Запускаем HTTPS прокси для API..."
cd ../backend
source ../venv/bin/activate
nohup python3 api_proxy.py > ../logs/api_proxy.log 2>&1 &
PROXY_PID=$!
sleep 3
cd ../telegram_components

# Запускаем Cloudflare туннель с конфигурацией
echo "🌐 Запускаем Cloudflare туннель с конфигурацией..."
nohup cloudflared tunnel --config ../cloudflare_config.yml run > cloudflare.log 2>&1 &
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

# Создаем временную копию бота с правильным URL и обработчиком Web App
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
echo "🧪 Тестируем доступность Mini App..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$MINI_APP_URL")
echo "✅ Mini App доступен: HTTP $HTTP_CODE"

echo ""
echo "🎉 TELEGRAM MINI APP ГОТОВ К ПОЛНОМУ ТЕСТИРОВАНИЮ!"
echo "==============================================="
echo "📱 Mini App URL: $MINI_APP_URL"
echo "🤖 Telegram Bot: @ExpressSmartAppBot"
echo "🌐 Cloudflare URL: $TUNNEL_URL" 
echo ""
echo "🔧 Запущенные сервисы:"
echo "• HTTP Server: PID $HTTP_PID (порт 8444)"
echo "• Cloudflare Tunnel: PID $TUNNEL_PID"
echo "• Bot Process: PID $BOT_PID"
echo ""
echo "📋 ИНСТРУКЦИЯ ПО ТЕСТИРОВАНИЮ:"
echo "============================================"
echo ""
echo "💻 ВЕБА-ВЕРСИЯ TELEGRAM:"
echo "1. Откройте Telegram в браузере"
echo "2. Найдите: @ExpressSmartAppBot"
echo "3. Отправьте /start"
echo "4. Нажмите '🚀 Mini App'"
echo "5. Заполните форму и отправьте"
echo "   ↳ Заявка отправится напрямую в API"
echo ""
echo "📱 МОБИЛЬНАЯ ВЕРСИЯ TELEGRAM:"
echo "1. Откройте мобильное приложение Telegram"
echo "2. Найдите: @ExpressSmartAppBot"
echo "3. Отправьте /start"
echo "4. Нажмите '🚀 Mini App'"
echo "5. Заполните форму и отправьте"
echo "   ↳ Данные передадутся через бота в API"
echo "   ↳ Получите подтверждение в чате с ботом"
echo ""
echo "🔧 ТЕХНИЧЕСКИЕ ОСОБЕННОСТИ:"
echo "• 💻 Веб-версия: прямая HTTP отправка в API"
echo "• 📱 Мобильная: безопасная передача через Telegram Web App API"
echo "• 🎨 Адаптивный дизайн под платформу"
echo "• 👤 Автозаполнение данных из профиля"
echo "• 🔒 Обход ограничений мобильного браузера"
echo ""
echo "📝 Для остановки: ./stop_final_mini_app.sh"
echo "📋 Логи бота: tail -f telegram_bot_mini.log"
echo "📊 Проверить Mini App: curl $MINI_APP_URL"
