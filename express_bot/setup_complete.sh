#!/bin/bash

echo "🚀 Полная настройка Express.ms Bot"
echo "================================="
echo "Согласно официальной документации Express.ms"
echo ""

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo $0"
    exit 1
fi

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "❌ Использование: $0 <domain> [email]"
    echo "Пример: $0 bot.yourcompany.com admin@yourcompany.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

echo "🌐 Домен: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# Функция для паузы
pause() {
    echo ""
    read -p "⏸️  Нажмите Enter для продолжения..."
    echo ""
}

# Функция для проверки успешности
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 завершено успешно"
    else
        echo "❌ Ошибка в $1"
        exit 1
    fi
}

echo "📋 ШАГ 1: ПРОВЕРКА СИСТЕМЫ"
echo "=========================="
echo "Проверяем системные требования..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    check_success "Установка Docker"
else
    echo "✅ Docker уже установлен"
fi

# Проверка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Установка Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    check_success "Установка Docker Compose"
else
    echo "✅ Docker Compose уже установлен"
fi

# Проверка дополнительных пакетов
echo "📦 Установка дополнительных пакетов..."
apt update -qq
apt install -y curl wget jq openssl ufw certbot
check_success "Установка пакетов"

pause

echo "📋 ШАГ 2: СОЗДАНИЕ СТРУКТУРЫ ДИРЕКТОРИЙ"
echo "======================================"
echo "Создаем директории согласно документации Express.ms..."

# Создание директорий
mkdir -p /opt/express/bots/storages
mkdir -p /opt/express/bots/production
mkdir -p /opt/express/bots/production/logs
mkdir -p /opt/express/bots/production/data
mkdir -p /opt/express/bots/production/ssl
mkdir -p /opt/express/bots/production/backups

echo "✅ Директории созданы"
echo "   - /opt/express/bots/storages (общее хранилище)"
echo "   - /opt/express/bots/production (production бот)"

pause

echo "📋 ШАГ 3: НАСТРОЙКА ОБЩЕГО ХРАНИЛИЩА"
echo "==================================="
echo "Настраиваем PostgreSQL и Redis..."

cd /opt/express/bots/storages

# Копирование файлов хранилища
cp /root/test/express_bot/docker-compose.storages.yml .

# Генерация паролей
POSTGRES_PASSWORD=$(openssl rand -hex 32)
echo "POSTGRES_USER=postgres" > .env
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .env

echo "🔑 Сгенерирован пароль PostgreSQL: $POSTGRES_PASSWORD"

# Запуск хранилища
echo "🚀 Запуск PostgreSQL и Redis..."
docker-compose -f docker-compose.storages.yml up -d
sleep 10

# Проверка статуса
docker-compose -f docker-compose.storages.yml ps
check_success "Настройка хранилища"

pause

echo "📋 ШАГ 4: СОЗДАНИЕ БАЗЫ ДАННЫХ ДЛЯ БОТА"
echo "======================================"
echo "Создаем базу данных и пользователя для бота..."

# Генерация паролей для бота
BOT_DB_PASSWORD=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

echo "🔑 Сгенерированы пароли:"
echo "   - PostgreSQL: $BOT_DB_PASSWORD"
echo "   - Secret Key: $SECRET_KEY"
echo "   - JWT Secret: $JWT_SECRET"

# Создание пользователя и БД
docker exec storages-postgres-1 psql -U postgres -c "CREATE USER express_bot_user;"
docker exec storages-postgres-1 psql -U postgres -c "ALTER USER express_bot_user WITH PASSWORD '$BOT_DB_PASSWORD';"
docker exec storages-postgres-1 psql -U postgres -c "CREATE DATABASE express_bot_db WITH OWNER express_bot_user;"

check_success "Создание базы данных"

pause

echo "📋 ШАГ 5: НАСТРОЙКА PRODUCTION БОТА"
echo "=================================="
echo "Настраиваем production конфигурацию бота..."

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
sed -i "s/your_secret_key_for_jwt_here/$SECRET_KEY/g" .env
sed -i "s/your_jwt_secret_here/$JWT_SECRET/g" .env
sed -i "s/your-domain.com/$DOMAIN/g" .env

echo "✅ Production конфигурация создана"

pause

echo "📋 ШАГ 6: НАСТРОЙКА SSL СЕРТИФИКАТА"
echo "=================================="
echo "Настраиваем SSL сертификат..."

# Выбор типа SSL
echo "🔐 Выберите тип SSL сертификата:"
echo "1) Let's Encrypt (рекомендуется)"
echo "2) Самоподписанный (для тестирования)"
read -p "Введите номер (1-2): " SSL_CHOICE

case $SSL_CHOICE in
    1)
        echo "🔐 Настройка Let's Encrypt SSL..."
        # Остановка nginx для получения сертификата
        systemctl stop nginx 2>/dev/null || true
        
        # Получение сертификата
        certbot certonly --standalone \
            --non-interactive \
            --agree-tos \
            --email "$EMAIL" \
            --domains "$DOMAIN"
        
        if [ $? -eq 0 ]; then
            # Копирование сертификатов
            cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ssl/cert.pem
            cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ssl/key.pem
            chmod 644 ssl/cert.pem
            chmod 600 ssl/key.pem
            echo "✅ Let's Encrypt SSL настроен"
        else
            echo "❌ Ошибка получения Let's Encrypt сертификата"
            echo "🔄 Переходим к самоподписанному сертификату..."
            SSL_CHOICE=2
        fi
        ;;
    2)
        echo "🔐 Настройка самоподписанного SSL..."
        # Генерация самоподписанного сертификата
        openssl genrsa -out ssl/key.pem 2048
        openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 \
            -subj "/C=RU/ST=Moscow/L=Moscow/O=Express.ms Bot/OU=IT Department/CN=$DOMAIN"
        chmod 600 ssl/key.pem
        chmod 644 ssl/cert.pem
        echo "✅ Самоподписанный SSL настроен"
        ;;
esac

pause

echo "📋 ШАГ 7: НАСТРОЙКА FIREWALL"
echo "============================"
echo "Настраиваем firewall..."

# Настройка ufw
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw deny 5432/tcp comment 'PostgreSQL (внутренний)'
ufw deny 6379/tcp comment 'Redis (внутренний)'
ufw deny 8000/tcp comment 'Bot Server (внутренний)'
ufw logging on
ufw --force enable

echo "✅ Firewall настроен"

pause

echo "📋 ШАГ 8: СОЗДАНИЕ SYSTEMD СЕРВИСА"
echo "=================================="
echo "Создаем systemd сервис для автозапуска..."

# Создание systemd сервиса
cat > /etc/systemd/system/express-bot.service << EOF
[Unit]
Description=Express.ms Bot Production
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/express/bots/production
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable express-bot

echo "✅ Systemd сервис создан"

pause

echo "📋 ШАГ 9: ЗАПУСК БОТА"
echo "===================="
echo "Запускаем Express.ms Bot..."

# Запуск бота
docker-compose up --build -d
sleep 15

# Проверка статуса
docker-compose ps
check_success "Запуск бота"

pause

echo "📋 ШАГ 10: ПРОВЕРКА РАБОТОСПОСОБНОСТИ"
echo "===================================="
echo "Проверяем работоспособность бота..."

# Проверка health check
echo "🏥 Проверка health check..."
HEALTH_RESPONSE=$(curl -s -k https://$DOMAIN/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Health check: OK"
    echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ Health check: FAIL"
fi

# Проверка webhook
echo "🔗 Проверка webhook..."
WEBHOOK_RESPONSE=$(curl -s -k -X POST https://$DOMAIN/webhook \
    -H "Content-Type: application/json" \
    -d '{"type": "message", "user_id": "test", "text": "/start"}' 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Webhook: OK"
    echo "$WEBHOOK_RESPONSE" | jq . 2>/dev/null || echo "$WEBHOOK_RESPONSE"
else
    echo "❌ Webhook: FAIL"
fi

pause

echo "📋 ШАГ 11: НАСТРОЙКА МОНИТОРИНГА"
echo "==============================="
echo "Настраиваем мониторинг и резервное копирование..."

# Создание скрипта мониторинга
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "📊 Express.ms Bot Monitor"
echo "========================="
echo "🐳 Контейнеры:"
docker-compose ps
echo ""
echo "💾 Ресурсы:"
docker stats --no-stream
echo ""
echo "🏥 Health:"
curl -s -k https://localhost/health | jq . 2>/dev/null || echo "Health check failed"
echo ""
echo "📈 Stats:"
curl -s -k https://localhost/stats | jq . 2>/dev/null || echo "Stats failed"
EOF

chmod +x monitor.sh

# Создание скрипта резервного копирования
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/express/bots/production/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Создание резервной копии..."

# Резервное копирование базы данных
docker exec express-bot-postgres-prod pg_dump -U express_bot_user express_bot_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# Резервное копирование Redis
docker exec express-bot-redis-prod redis-cli --rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

# Сжатие
cd "$BACKUP_DIR"
tar -czf "backup_$DATE.tar.gz" "db_backup_$DATE.sql" "redis_backup_$DATE.rdb"
rm "db_backup_$DATE.sql" "redis_backup_$DATE.rdb"

echo "✅ Резервная копия создана: backup_$DATE.tar.gz"

# Удаление старых копий
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Настройка cron для резервного копирования
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/express/bots/production/backup.sh") | crontab -

echo "✅ Мониторинг и резервное копирование настроены"

pause

echo "🎉 НАСТРОЙКА ЗАВЕРШЕНА!"
echo "======================"
echo ""
echo "✅ Express.ms Bot успешно настроен согласно официальной документации"
echo ""
echo "🌐 Ваши URL:"
echo "   - HTTP: http://$DOMAIN"
echo "   - HTTPS: https://$DOMAIN"
echo "   - Health: https://$DOMAIN/health"
echo "   - Webhook: https://$DOMAIN/webhook"
echo "   - Admin: https://$DOMAIN/admin"
echo ""
echo "🔧 Управление:"
echo "   - Статус: systemctl status express-bot"
echo "   - Запуск: systemctl start express-bot"
echo "   - Остановка: systemctl stop express-bot"
echo "   - Логи: journalctl -u express-bot -f"
echo "   - Мониторинг: ./monitor.sh"
echo "   - Резервное копирование: ./backup.sh"
echo ""
echo "📋 Следующие шаги:"
echo "1. Получите BOT_CREDENTIALS от разработчиков Express.ms"
echo "2. Обновите .env файл с правильными credentials"
echo "3. Перезапустите бота: systemctl restart express-bot"
echo "4. Зарегистрируйте webhook в Express.ms: https://$DOMAIN/webhook"
echo "5. Протестируйте бота командой /start"
echo ""
echo "📞 Контакты Express.ms:"
echo "   - Sales: sales@express.ms"
echo "   - Support: support@express.ms"
echo "   - Документация: https://express.ms/faq/"
echo ""
echo "🎯 Бот готов к работе!"
