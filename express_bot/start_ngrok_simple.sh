#!/bin/bash

# Простой запуск ngrok для Express Bot

echo "🚀 Запуск ngrok для Express Bot..."

# Проверяем наличие ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен. Устанавливаем..."
    wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
    unzip /tmp/ngrok.zip -d /usr/local/bin/
    chmod +x /usr/local/bin/ngrok
    rm /tmp/ngrok.zip
    echo "✅ ngrok установлен"
fi

# Проверяем, настроен ли authtoken
if ! ngrok config check &> /dev/null; then
    echo "🔑 ngrok требует аутентификации."
    echo "Получите authtoken на: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo ""
    read -p "Введите ваш ngrok authtoken: " NGROK_TOKEN
    
    if [ -z "$NGROK_TOKEN" ]; then
        echo "❌ Authtoken не введен. Выход."
        exit 1
    fi
    
    ngrok config add-authtoken $NGROK_TOKEN
    echo "✅ ngrok настроен"
fi

# Запускаем ngrok
echo "🌐 Запускаем ngrok туннель на порт 8000..."
ngrok http 8000 --log=stdout
