#!/bin/bash
"""
Быстрый запуск ngrok для Express Bot
"""

echo "🚀 Запуск ngrok для Express Bot..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Останавливаем старые туннели
echo "🛑 Останавливаем старые туннели..."
pkill cloudflared 2>/dev/null || true
pkill ngrok 2>/dev/null || true
sleep 2

# Проверяем, что бот запущен
echo "🔍 Проверяем статус бота..."
if ! pgrep -f "express_bot_with_admin" > /dev/null; then
    echo "❌ Бот не запущен! Запускаем..."
    python3 express_bot_with_admin.py &
    sleep 3
fi

# Устанавливаем ngrok если не установлен
if ! command -v ngrok &> /dev/null; then
    echo "📦 Устанавливаем ngrok..."
    wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
    unzip /tmp/ngrok.zip -d /usr/local/bin/
    chmod +x /usr/local/bin/ngrok
    echo "✅ ngrok установлен"
fi

# Запускаем ngrok
echo "🚀 Запускаем ngrok туннель..."
ngrok http 5010 --log=stdout &
NGROK_PID=$!

# Ждем запуска
sleep 5

# Получаем URL туннеля
echo "🔍 Получаем URL туннеля..."
sleep 3

# Пробуем получить URL через API
TUNNEL_URL=""
if command -v curl &> /dev/null; then
    TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

if [ -z "$TUNNEL_URL" ]; then
    echo "⚠️ Не удалось получить URL автоматически"
    echo "📋 Проверьте ngrok веб-интерфейс: http://localhost:4040"
    echo "📋 Или найдите URL в логах ngrok"
else
    echo "✅ Туннель создан: $TUNNEL_URL"
    echo "🌐 Webhook URL: $TUNNEL_URL/webhook"
    echo "👨‍💼 Admin Panel: $TUNNEL_URL/admin"
    
    # Обновляем конфигурацию
    echo "⚙️ Обновляем конфигурацию..."
    if [ -f "config.json" ]; then
        sed -i "s|\"webhook_url\": \".*\"|\"webhook_url\": \"$TUNNEL_URL/webhook\"|g" config.json
        echo "✅ Конфигурация обновлена"
    fi
fi

echo ""
echo "🎉 ngrok запущен!"
echo "📊 ngrok веб-интерфейс: http://localhost:4040"
echo "🤖 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99"
echo "🔗 Health Check: $TUNNEL_URL/health"
echo "📋 Manifest: $TUNNEL_URL/manifest"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте админ панель Express.ms"
echo "2. Добавьте бота как SmartApp"
echo "3. Укажите webhook URL: $TUNNEL_URL/webhook"
echo "4. Протестируйте команду /start"
echo ""
echo "🛑 Для остановки: pkill ngrok"
echo "📝 Логи: tail -f /root/test/express_bot/fixed_bot.log"


