#!/bin/bash

echo "🎉 Финальное тестирование CloudPub Express Bot"
echo "=============================================="

CLOUDPUB_URL="https://loosely-welcoming-grackle.cloudpub.ru"
LOCAL_URL="http://localhost:5011"

echo "🌐 CloudPub URL: $CLOUDPUB_URL"
echo "🏠 Local URL: $LOCAL_URL"
echo ""

# Тестируем локальный бот
echo "1️⃣ Тестируем локальный бот..."
LOCAL_HEALTH=$(curl -s $LOCAL_URL/health | jq -r '.status' 2>/dev/null)
if [ "$LOCAL_HEALTH" = "healthy" ]; then
    echo "✅ Локальный бот: OK"
else
    echo "❌ Локальный бот: FAIL"
fi

# Тестируем CloudPub
echo ""
echo "2️⃣ Тестируем CloudPub..."
CLOUDPUB_HEALTH=$(curl -s $CLOUDPUB_URL/health | jq -r '.status' 2>/dev/null)
if [ "$CLOUDPUB_HEALTH" = "healthy" ]; then
    echo "✅ CloudPub: OK"
else
    echo "❌ CloudPub: FAIL"
fi

# Тестируем webhook
echo ""
echo "3️⃣ Тестируем webhook..."
WEBHOOK_RESPONSE=$(curl -s -X POST $CLOUDPUB_URL/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}' | jq -r '.status' 2>/dev/null)
if [ "$WEBHOOK_RESPONSE" = "ok" ]; then
    echo "✅ Webhook: OK"
else
    echo "❌ Webhook: FAIL"
fi

echo ""
echo "=============================================="
echo "📊 РЕЗУЛЬТАТЫ:"
echo "=============================================="
echo "🏠 Локальный бот: $([ "$LOCAL_HEALTH" = "healthy" ] && echo "✅ OK" || echo "❌ FAIL")"
echo "🌐 CloudPub: $([ "$CLOUDPUB_HEALTH" = "healthy" ] && echo "✅ OK" || echo "❌ FAIL")"
echo "🔗 Webhook: $([ "$WEBHOOK_RESPONSE" = "ok" ] && echo "✅ OK" || echo "❌ FAIL")"

if [ "$LOCAL_HEALTH" = "healthy" ] && [ "$CLOUDPUB_HEALTH" = "healthy" ] && [ "$WEBHOOK_RESPONSE" = "ok" ]; then
    echo ""
    echo "🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!"
    echo ""
    echo "📱 Настройка в Express.ms:"
    echo "1. Откройте админ панель Express.ms"
    echo "2. Добавьте бота как SmartApp"
    echo "3. Укажите webhook URL: $CLOUDPUB_URL/webhook"
    echo "4. Протестируйте команду /start"
    echo ""
    echo "🌐 Ваши URL:"
    echo "   Bot URL: $CLOUDPUB_URL"
    echo "   Webhook: $CLOUDPUB_URL/webhook"
    echo "   Admin: $CLOUDPUB_URL/admin"
else
    echo ""
    echo "❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ"
    echo "Проверьте логи и настройки"
fi

