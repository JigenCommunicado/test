#!/bin/bash

echo "🚀 Упрощенная настройка Express.ms Bot"
echo "===================================="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo $0"
    exit 1
fi

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "❌ Использование: $0 <domain>"
    echo "Пример: $0 bot.yourcompany.com"
    exit 1
fi

DOMAIN=$1

echo "🌐 Домен: $DOMAIN"
echo ""

# Шаг 1: Создание директорий
echo "📁 ШАГ 1: Создание директорий..."
mkdir -p /opt/express/bots/storages
mkdir -p /opt/express/bots/production
mkdir -p /opt/express/bots/production/{logs,data,ssl,backups}
echo "✅ Директории созданы"

# Шаг 2: Настройка хранилища
echo ""
echo "🗄️ ШАГ 2: Настройка хранилища..."
cd /opt/express/bots/storages

# Копирование файлов
cp /root/test/express_bot/docker-compose.storages.yml .

# Создание .env для хранилища
POSTGRES_PASSWORD=$(openssl rand -hex 32)
cat > .env << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
EOF

echo "🔑 Пароль PostgreSQL: $POSTGRES_PASSWORD"

# Запуск хранилища
echo "🚀 Запуск PostgreSQL и Redis..."
docker-compose -f docker-compose.storages.yml up -d
sleep 10

# Проверка статуса
echo "📊 Статус хранилища:"
docker-compose -f docker-compose.storages.yml ps

# Шаг 3: Создание базы данных для бота
echo ""
echo "🗄️ ШАГ 3: Создание базы данных для бота..."
BOT_DB_PASSWORD=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)

echo "🔑 Пароль БД бота: $BOT_DB_PASSWORD"
echo "🔑 Secret Key: $SECRET_KEY"

# Создание пользователя и БД
docker exec storages-postgres-1 psql -U postgres -c "CREATE USER express_bot_user;"
docker exec storages-postgres-1 psql -U postgres -c "ALTER USER express_bot_user WITH PASSWORD '$BOT_DB_PASSWORD';"
docker exec storages-postgres-1 psql -U postgres -c "CREATE DATABASE express_bot_db WITH OWNER express_bot_user;"

# Шаг 4: Настройка production бота
echo ""
echo "🤖 ШАГ 4: Настройка production бота..."
cd /opt/express/bots/production

# Копирование файлов
cp /root/test/express_bot/docker-compose.prod.yml docker-compose.yml
cp /root/test/express_bot/Dockerfile.prod Dockerfile
cp /root/test/express_bot/requirements.txt .
cp /root/test/express_bot/express_bot_docker.py .
cp /root/test/express_bot/init.sql .
cp /root/test/express_bot/nginx.conf .
cp /root/test/express_bot/postgresql.conf .
cp /root/test/express_bot/redis.conf .
cp /root/test/express_bot/env.prod .env

# Обновление .env файла
sed -i "s/your_secure_postgres_password_here/$BOT_DB_PASSWORD/g" .env
sed -i "s/your-domain.com/$DOMAIN/g" .env
sed -i "s/your_secret_key_for_jwt_here/$SECRET_KEY/g" .env

echo "✅ Production конфигурация создана"

# Шаг 5: Настройка SSL
echo ""
echo "🔐 ШАГ 5: Настройка SSL сертификата..."
mkdir -p ssl

# Создание самоподписанного сертификата
openssl genrsa -out ssl/key.pem 2048
openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Express.ms Bot/OU=IT Department/CN=$DOMAIN"
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "✅ SSL сертификат создан"

# Шаг 6: Запуск бота
echo ""
echo "🚀 ШАГ 6: Запуск бота..."
docker-compose up --build -d
sleep 15

# Проверка статуса
echo "📊 Статус бота:"
docker-compose ps

# Шаг 7: Проверка работоспособности
echo ""
echo "🏥 ШАГ 7: Проверка работоспособности..."

# Проверка health check
echo "🔍 Проверка health check..."
HEALTH_RESPONSE=$(curl -s -k https://$DOMAIN/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Health check: OK"
    echo "$HEALTH_RESPONSE" | head -3
else
    echo "❌ Health check: FAIL"
fi

# Проверка webhook
echo "🔍 Проверка webhook..."
WEBHOOK_RESPONSE=$(curl -s -k -X POST https://$DOMAIN/webhook \
    -H "Content-Type: application/json" \
    -d '{"type": "message", "user_id": "test", "text": "/start"}' 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Webhook: OK"
    echo "$WEBHOOK_RESPONSE" | head -3
else
    echo "❌ Webhook: FAIL"
fi

echo ""
echo "🎉 НАСТРОЙКА ЗАВЕРШЕНА!"
echo "======================"
echo ""
echo "🌐 Ваши URL:"
echo "   - HTTP: http://$DOMAIN"
echo "   - HTTPS: https://$DOMAIN"
echo "   - Health: https://$DOMAIN/health"
echo "   - Webhook: https://$DOMAIN/webhook"
echo "   - Admin: https://$DOMAIN/admin"
echo ""
echo "🔧 Управление:"
echo "   - Статус: cd /opt/express/bots/production && docker-compose ps"
echo "   - Логи: cd /opt/express/bots/production && docker-compose logs -f"
echo "   - Остановка: cd /opt/express/bots/production && docker-compose down"
echo "   - Перезапуск: cd /opt/express/bots/production && docker-compose restart"
echo ""
echo "📋 Следующие шаги:"
echo "1. Получите BOT_CREDENTIALS от разработчиков Express.ms"
echo "2. Обновите .env файл: nano /opt/express/bots/production/.env"
echo "3. Перезапустите бота: cd /opt/express/bots/production && docker-compose restart"
echo "4. Зарегистрируйте webhook в Express.ms: https://$DOMAIN/webhook"
echo ""
echo "🎯 Бот готов к работе!"
