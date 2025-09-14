#!/bin/bash

# Скрипт для запуска тестов Express SmartApp
# Автор: AI Assistant
# Дата: $(date)

echo "🧪 Запуск тестов Express SmartApp..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Проверяем, что серверы запущены
echo "🔍 Проверка серверов..."

# Проверяем Flask сервер
if ! curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "❌ Flask сервер не запущен на порту 5002"
    echo "   Запустите серверы: ./manage.sh"
    exit 1
fi

# Проверяем статический сервер
if ! curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "❌ Статический сервер не запущен на порту 8080"
    echo "   Запустите серверы: ./manage.sh"
    exit 1
fi

echo "✅ Серверы запущены"

# Активируем виртуальное окружение
echo "🐍 Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем зависимости для тестирования
echo "📦 Установка зависимостей для тестирования..."
pip install -q requests

# Запускаем тесты
echo "🚀 Запуск тестов..."
python3 test_suite.py

# Проверяем результат
if [ $? -eq 0 ]; then
    echo "✅ Все тесты пройдены успешно!"
else
    echo "❌ Некоторые тесты провалились"
    exit 1
fi

echo "🎉 Тестирование завершено!"

