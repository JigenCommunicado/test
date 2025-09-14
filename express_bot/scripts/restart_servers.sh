#!/bin/bash

# Скрипт для перезапуска всех серверов Express SmartApp
# Автор: AI Assistant
# Дата: $(date)

echo "🔄 Перезапуск Express SmartApp серверов..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Останавливаем серверы
echo "🛑 Остановка серверов..."
./stop_servers.sh

# Ждем полной остановки
sleep 3

# Запускаем серверы
echo "🚀 Запуск серверов..."
./start_servers.sh

echo ""
echo "🎉 Перезапуск завершен!"

