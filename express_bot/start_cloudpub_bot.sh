#!/bin/bash

echo "🚀 Запуск Express Bot с CloudPub..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Проверяем, что CloudPub работает
echo "1️⃣ Проверяем статус CloudPub..."
sudo clo ls

# Проверяем, что порт 5011 свободен
echo "2️⃣ Проверяем порт 5011..."
if lsof -Pi :5011 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Порт 5011 занят, останавливаем старый процесс..."
    pkill -f "express_bot_cloudpub.py"
    sleep 2
fi

# Устанавливаем зависимости
echo "3️⃣ Устанавливаем зависимости..."
pip install flask aiohttp

# Запускаем бота
echo "4️⃣ Запускаем Express Bot с CloudPub..."
python3 express_bot_cloudpub.py > cloudpub_bot.log 2>&1 &

# Получаем PID процесса
BOT_PID=$!
echo "📱 Bot PID: $BOT_PID"

# Ждем запуска
echo "5️⃣ Ждем запуска бота..."
sleep 5

# Проверяем, что бот запустился
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Express Bot успешно запущен!"
    echo "📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99"
    echo "🌐 CloudPub URL: https://loosely-welcoming-grackle.cloudpub.ru"
    echo "🔗 Webhook URL: https://loosely-welcoming-grackle.cloudpub.ru/webhook"
    echo "👨‍💼 Admin Panel: https://loosely-welcoming-grackle.cloudpub.ru/admin"
    echo "📊 Логи: tail -f /root/test/express_bot/cloudpub_bot.log"
    
    # Тестируем подключение
    echo "6️⃣ Тестируем подключение..."
    sleep 3
    
    # Health check
    echo "🏥 Health check:"
    curl -s https://loosely-welcoming-grackle.cloudpub.ru/health | head -3
    
    echo ""
    echo "🧪 Webhook test:"
    curl -X POST https://loosely-welcoming-grackle.cloudpub.ru/webhook \
      -H "Content-Type: application/json" \
      -d '{"type": "message", "user_id": "test", "text": "/start"}' \
      -s | head -3
    
    echo ""
    echo "🎉 Express Bot готов к работе с CloudPub!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Откройте админ панель Express.ms"
    echo "2. Добавьте бота как SmartApp"
    echo "3. Укажите webhook URL: https://loosely-welcoming-grackle.cloudpub.ru/webhook"
    echo "4. Протестируйте команду /start"
    
else
    echo "❌ Ошибка запуска Express Bot"
    echo "📋 Проверьте логи: cat /root/test/express_bot/cloudpub_bot.log"
fi

# Сохраняем PID для остановки
echo $BOT_PID > /root/test/express_bot/cloudpub_bot.pid
echo "💾 PID сохранен в cloudpub_bot.pid"
