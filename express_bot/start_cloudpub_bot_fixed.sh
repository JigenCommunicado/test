#!/bin/bash

echo "🚀 Запуск Express Bot с CloudPub (исправленная версия)..."

# Переходим в директорию проекта
cd /root/test/express_bot

# 1. Останавливаем все процессы бота
echo "1️⃣ Останавливаем старые процессы..."
pkill -f "express_bot_cloudpub.py" 2>/dev/null || echo "Старые процессы не найдены"

# 2. Принудительно освобождаем порт 5011
echo "2️⃣ Освобождаем порт 5011..."
fuser -k 5011/tcp 2>/dev/null || echo "Порт 5011 свободен"

# 3. Ждем освобождения порта
echo "3️⃣ Ждем освобождения порта..."
sleep 3

# 4. Проверяем, что порт свободен
if lsof -Pi :5011 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Порт 5011 все еще занят, принудительно освобождаем..."
    fuser -k 5011/tcp
    sleep 2
fi

# 5. Проверяем статус CloudPub
echo "4️⃣ Проверяем статус CloudPub..."
sudo clo ls

# 6. Запускаем бота в фоне
echo "5️⃣ Запускаем Express Bot..."
nohup python3 express_bot_cloudpub.py > cloudpub_bot.log 2>&1 &

# Получаем PID
BOT_PID=$!
echo "📱 Bot PID: $BOT_PID"

# 7. Ждем запуска
echo "6️⃣ Ждем запуска бота..."
sleep 5

# 8. Проверяем, что бот запустился
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Express Bot успешно запущен!"
    echo "📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99"
    echo "🌐 CloudPub URL: https://loosely-welcoming-grackle.cloudpub.ru"
    echo "🔗 Webhook URL: https://loosely-welcoming-grackle.cloudpub.ru/webhook"
    echo "👨‍💼 Admin Panel: https://loosely-welcoming-grackle.cloudpub.ru/admin"
    echo "📊 Логи: tail -f /root/test/express_bot/cloudpub_bot.log"
    
    # Сохраняем PID
    echo $BOT_PID > cloudpub_bot.pid
    
    # 9. Тестируем подключение
    echo "7️⃣ Тестируем подключение..."
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
    exit 1
fi
