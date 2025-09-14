#!/bin/bash

echo "🚀 Настройка Express.ms Bot для Docker"
echo "======================================"

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и повторите попытку."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и повторите попытку."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создание директорий
echo "📁 Создание директорий..."
mkdir -p /opt/express/bots/storages
mkdir -p /opt/express/bots/express-bot
mkdir -p logs

# Копирование файлов
echo "📋 Копирование файлов..."
cp docker-compose.storages.yml /opt/express/bots/storages/
cp docker-compose.yml /opt/express/bots/express-bot/
cp Dockerfile /opt/express/bots/express-bot/
cp requirements.txt /opt/express/bots/express-bot/
cp express_bot_docker.py /opt/express/bots/express-bot/
cp init.sql /opt/express/bots/express-bot/
cp env.example /opt/express/bots/express-bot/.env

# Настройка хранилища
echo "🗄️ Настройка общего хранилища..."
cd /opt/express/bots/storages

# Генерация пароля для PostgreSQL
POSTGRES_PASSWORD=$(openssl rand -hex 32)
echo "POSTGRES_USER=postgres" > .env
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .env

# Запуск хранилища
echo "🚀 Запуск PostgreSQL и Redis..."
docker-compose -f docker-compose.storages.yml up -d

# Ожидание запуска
echo "⏳ Ожидание запуска хранилища..."
sleep 10

# Проверка статуса
echo "🔍 Проверка статуса хранилища..."
docker-compose -f docker-compose.storages.yml ps

# Создание базы данных для бота
echo "🗄️ Создание базы данных для бота..."
BOT_DB_PASSWORD=$(openssl rand -hex 32)

docker exec storages-postgres-1 psql -U postgres -c "CREATE USER express_bot_user;"
docker exec storages-postgres-1 psql -U postgres -c "ALTER USER express_bot_user WITH PASSWORD '$BOT_DB_PASSWORD';"
docker exec storages-postgres-1 psql -U postgres -c "CREATE DATABASE express_bot_db WITH OWNER express_bot_user;"

# Настройка бота
echo "🤖 Настройка бота..."
cd /opt/express/bots/express-bot

# Обновление .env файла
sed -i "s/your_secure_password_here/$BOT_DB_PASSWORD/g" .env
sed -i "s|postgresql://express_bot_user:your_secure_password_here@postgres:5432/express_bot_db|postgresql://express_bot_user:$BOT_DB_PASSWORD@postgres:5432/express_bot_db|g" .env

echo "✅ Настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте /opt/express/bots/express-bot/.env"
echo "2. Укажите правильные BOT_CREDENTIALS и HOST"
echo "3. Запустите бота: cd /opt/express/bots/express-bot && docker-compose up -d"
echo ""
echo "🌐 После запуска бот будет доступен на:"
echo "   - Health: http://localhost:8000/health"
echo "   - Manifest: http://localhost:8000/manifest"
echo "   - Stats: http://localhost:8000/stats"
echo ""
echo "📞 Для получения BOT_CREDENTIALS обратитесь к разработчикам Express.ms"
