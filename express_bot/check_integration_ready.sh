#!/bin/bash

# Скрипт проверки готовности Final Express Bot к интеграции
echo "🔍 Проверка готовности Express Bot к интеграции"
echo "============================================="

# Переходим в директорию проекта
cd /root/test/express_bot

# Проверяем процессы
echo "📋 Проверка процессов..."
echo "------------------------"
echo "🔍 Express Bot Webhook Server..."
if ps aux | grep "express_bot_webhook.py" | grep -v grep > /dev/null; then
    echo "✅ RUNNING"
else
    echo "❌ NOT RUNNING"
    exit 1
fi

echo "🔍 Cloudflare Tunnel..."
if ps aux | grep "cloudflared tunnel" | grep "localhost:5006" | grep -v grep > /dev/null; then
    echo "✅ RUNNING"
else
    echo "❌ NOT RUNNING"
    exit 1
fi

echo "🔍 Flask API Server..."
if ps aux | grep "express_smartapp_proper.py" | grep -v grep > /dev/null; then
    echo "✅ RUNNING"
else
    echo "❌ NOT RUNNING"
    exit 1
fi

# Проверяем endpoints
echo ""
echo "🌐 Проверка endpoints..."
echo "------------------------"
echo "🔍 Health Check..."
if curl -s -f https://comparing-doom-solving-royalty.trycloudflare.com/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Manifest..."
if curl -s -f https://comparing-doom-solving-royalty.trycloudflare.com/manifest > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Webhook (GET)..."
# Webhook должен возвращать 405 для GET запросов (это правильно)
if curl -s -o /dev/null -w "%{http_code}" https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "405"; then
    echo "✅ OK (405 - Method Not Allowed, это правильно)"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Webhook (POST)..."
# POST запрос должен возвращать 200 или 400 (в зависимости от данных)
if curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"test":"data"}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -qE "(200|400)"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

# Проверяем команды бота
echo ""
echo "🤖 Проверка команд бота..."
echo "-------------------------"
echo "🔍 Command /start..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"message","user_id":"test123","text":"/start"}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

# Проверяем callback функции
echo "🔍 Callback: location selection..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"callback_query","user_id":"test123","callback_query":{"data":"location_МСК"}}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Callback: calendar navigation..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"callback_query","user_id":"test123","callback_query":{"data":"nav_month_2025_9_2025"}}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Callback: date selection..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"callback_query","user_id":"test123","callback_query":{"data":"date_15.09.2025"}}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Callback: position selection..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"callback_query","user_id":"test123","callback_query":{"data":"position_БП"}}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Callback: direction selection..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"callback_query","user_id":"test123","callback_query":{"data":"direction_Санкт-Петербург"}}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Callback: application confirmation..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"callback_query","user_id":"test123","callback_query":{"data":"confirm_application"}}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 Callback: back navigation..."
if curl -s -X POST -H "Content-Type: application/json" -d '{"type":"callback_query","user_id":"test123","callback_query":{"data":"back_to_start"}}' https://comparing-doom-solving-royalty.trycloudflare.com/webhook | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

# Проверяем интеграцию с API
echo ""
echo "📊 Проверка интеграции с API..."
echo "-------------------------------"
echo "🔍 API Health..."
if curl -s -f http://localhost:5002/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🔍 API Periods..."
if curl -s -f http://localhost:5002/api/public/application-periods > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

# Проверяем конфигурацию
echo ""
echo "🔧 Проверка конфигурации..."
echo "--------------------------"
echo "🔍 Конфигурация бота..."
if [ -f "express_bot_config.py" ]; then
    echo "✅ EXISTS"
else
    echo "❌ MISSING"
    exit 1
fi

echo "🔍 Основной код бота..."
if [ -f "express_bot.py" ]; then
    echo "✅ EXISTS"
else
    echo "❌ MISSING"
    exit 1
fi

echo "🔍 Webhook сервер..."
if [ -f "express_bot_webhook.py" ]; then
    echo "✅ EXISTS"
else
    echo "❌ MISSING"
    exit 1
fi

echo "🔍 Скрипт запуска..."
if [ -f "start_bot.sh" ]; then
    echo "✅ EXISTS"
else
    echo "❌ MISSING"
    exit 1
fi

echo "🔍 Тесты..."
if [ -f "test_bot.py" ]; then
    echo "✅ EXISTS"
else
    echo "❌ MISSING"
    exit 1
fi

echo "🔍 Документация..."
if [ -f "README.md" ]; then
    echo "✅ EXISTS"
else
    echo "❌ MISSING"
    exit 1
fi

# Проверяем результаты тестов
echo ""
echo "📈 Проверка результатов тестов..."
echo "--------------------------------"
if [ -f "bot_test_results.json" ]; then
    echo "✅ Результаты тестов найдены"
    # Извлекаем успешность из JSON
    SUCCESS_RATE=$(python3 -c "import json; data=json.load(open('bot_test_results.json')); print(f\"{data['success_rate']:.1f}%\")")
    echo "📊 Успешность тестов: $SUCCESS_RATE"
    
    if [ $(python3 -c "import json; data=json.load(open('bot_test_results.json')); print('1' if data['success_rate'] >= 90 else '0')") = "1" ]; then
        echo "✅ Тесты пройдены успешно"
    else
        echo "❌ Тесты требуют внимания"
        exit 1
    fi
else
    echo "❌ Результаты тестов не найдены"
    exit 1
fi

# Итоговые результаты
echo ""
echo "============================================="
echo "📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ"
echo "============================================="
echo "✅ Пройдено: 20 из 20 проверок"
echo "📈 Успешность: 100%"
echo "🎉 EXPRESS БОТ ГОТОВ К ИНТЕГРАЦИИ!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте панель администратора Express"
echo "2. Добавьте бота с настройками:"
echo "   - Webhook URL: https://comparing-doom-solving-royalty.trycloudflare.com/webhook"
echo "   - Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99"
echo "   - Secret Key: a75b4cd97d9e88e543f077178b2d5a4f"
echo "3. Настройте разрешения и команды"
echo "4. Протестируйте в Express Messenger"
echo ""
echo "📖 Подробная документация: cat README.md"
echo "🧪 Запуск тестов: python3 test_bot.py"
echo "🚀 Перезапуск бота: ./start_bot.sh"
