#!/bin/bash
# Скрипт запуска правильного Express SmartApp согласно документации

echo "🚀 Запуск Express SmartApp (правильная версия)"
echo "=============================================="

cd /root/test/express_bot

# Проверяем Flask API
echo "🔍 Проверяем Flask API..."
if ! curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "❌ Flask API недоступен. Запустите сначала ./manage_all.sh start"
    exit 1
fi
echo "✅ Flask API работает"

# Останавливаем старую версию если запущена
echo "🔄 Останавливаем старую версию SmartApp..."
pkill -f express_smartapp.py
sleep 2

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем правильный Express SmartApp
echo "🚀 Запускаем правильный Express SmartApp..."
nohup python3 express_smartapp_proper.py > logs/express_smartapp_proper.log 2>&1 &
SMARTAPP_PID=$!
sleep 3

# Проверяем что SmartApp запустился
if ps -p $SMARTAPP_PID > /dev/null 2>&1; then
    echo "✅ Express SmartApp запущен (PID: $SMARTAPP_PID)"
else
    echo "❌ Express SmartApp не запустился. Проверьте логи:"
    cat logs/express_smartapp_proper.log
    exit 1
fi

# Тестируем доступность
echo "🧪 Тестируем доступность SmartApp..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5005/health)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Express SmartApp доступен: HTTP $HTTP_CODE"
else
    echo "❌ Express SmartApp недоступен: HTTP $HTTP_CODE"
fi

# Тестируем манифест
echo "📋 Тестируем манифест..."
MANIFEST_NAME=$(curl -s http://localhost:5005/manifest | jq -r '.name' 2>/dev/null)
if [ "$MANIFEST_NAME" != "null" ] && [ -n "$MANIFEST_NAME" ]; then
    echo "✅ Манифест работает: $MANIFEST_NAME"
else
    echo "❌ Манифест недоступен"
fi

echo ""
echo "🎉 EXPRESS SMARTAPP ГОТОВ К ИНТЕГРАЦИИ!"
echo "====================================="
echo "📱 SmartApp URL: http://localhost:5005/"
echo "🔗 API URL: http://localhost:5005/"
echo "📋 Манифест: http://localhost:5005/manifest"
echo "📊 Health Check: http://localhost:5005/health"
echo ""
echo "🔧 Интеграция с Express мессенджером:"
echo "1. Настройте Express сервер для подключения SmartApp"
echo "2. Укажите URL: http://localhost:5005/"
echo "3. Настройте webhook: http://localhost:5005/webhook"
echo "4. Используйте манифест: http://localhost:5005/manifest"
echo ""
echo "📋 Для остановки: ./stop_express_smartapp_proper.sh"
echo "📋 Логи: tail -f logs/express_smartapp_proper.log"







