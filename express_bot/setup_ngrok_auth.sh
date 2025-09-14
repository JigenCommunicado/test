#!/bin/bash

# Скрипт настройки ngrok с аутентификацией

echo "🔐 Настройка ngrok с аутентификацией..."

# Проверяем наличие ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен. Устанавливаем..."
    wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
    unzip /tmp/ngrok.zip -d /usr/local/bin/
    chmod +x /usr/local/bin/ngrok
    rm /tmp/ngrok.zip
    echo "✅ ngrok установлен"
fi

# Запрашиваем authtoken
echo ""
echo "🔑 Для работы ngrok нужен authtoken."
echo "Получите его на: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
read -p "Введите ваш ngrok authtoken: " NGROK_TOKEN

if [ -z "$NGROK_TOKEN" ]; then
    echo "❌ Authtoken не введен. Выход."
    exit 1
fi

# Настраиваем ngrok
echo "⚙️ Настраиваем ngrok..."
ngrok config add-authtoken $NGROK_TOKEN

# Обновляем конфигурацию ngrok.yml
echo "📝 Обновляем конфигурацию ngrok.yml..."
cat > ngrok.yml << EOF
version: "2"
authtoken: $NGROK_TOKEN
tunnels:
  express-bot:
    proto: http
    addr: localhost:8000
    inspect: true
    bind_tls: true
    web_addr: 0.0.0.0:4040
EOF

echo "✅ Конфигурация ngrok обновлена"

# Запускаем ngrok в фоне
echo "🚀 Запускаем ngrok туннель..."
ngrok start express-bot --config=ngrok.yml &
NGROK_PID=$!

# Ждем запуска
echo "⏳ Ожидаем запуска ngrok..."
sleep 5

# Получаем URL
echo "🌐 Получаем URL туннеля..."
for i in {1..10}; do
    if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('tunnels'):
        print(data['tunnels'][0]['public_url'])
except:
    pass
" 2>/dev/null)
        break
    fi
    sleep 2
done

if [ -n "$NGROK_URL" ]; then
    echo "✅ ngrok туннель создан: $NGROK_URL"
    echo "🌐 Webhook URL: $NGROK_URL/webhook"
    echo "📊 ngrok веб-интерфейс: http://localhost:4040"
    
    # Сохраняем URL в файл
    echo "NGROK_URL=$NGROK_URL" > .env.ngrok
    echo "✅ URL сохранен в .env.ngrok"
    
    echo ""
    echo "🎉 ngrok настроен и запущен!"
    echo "📋 Для остановки: kill $NGROK_PID"
    echo "📋 Для просмотра логов: curl http://localhost:4040/api/tunnels"
    
else
    echo "❌ Не удалось получить URL ngrok"
    echo "Проверьте логи: curl http://localhost:4040/api/tunnels"
fi
