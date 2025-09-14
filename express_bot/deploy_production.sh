#!/bin/bash

echo "🚀 Production развертывание Express.ms Bot"
echo "=========================================="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo $0"
    exit 1
fi

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
mkdir -p /opt/express/bots/production
mkdir -p /opt/express/bots/production/logs
mkdir -p /opt/express/bots/production/data
mkdir -p /opt/express/bots/production/ssl
mkdir -p /opt/express/bots/production/backups

# Копирование файлов
echo "📋 Копирование файлов..."
cp docker-compose.prod.yml /opt/express/bots/production/docker-compose.yml
cp Dockerfile /opt/express/bots/production/
cp requirements.txt /opt/express/bots/production/
cp express_bot_docker.py /opt/express/bots/production/
cp init.sql /opt/express/bots/production/
cp nginx.conf /opt/express/bots/production/
cp postgresql.conf /opt/express/bots/production/
cp redis.conf /opt/express/bots/production/
cp env.prod /opt/express/bots/production/.env

# Настройка SSL
echo "🔐 Настройка SSL сертификатов..."
cd /opt/express/bots/production
chmod +x ../../test/express_bot/setup_ssl.sh
../../test/express_bot/setup_ssl.sh

# Генерация паролей
echo "🔑 Генерация паролей..."
POSTGRES_PASSWORD=$(openssl rand -hex 32)
REDIS_PASSWORD=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Обновление .env файла
sed -i "s/your_secure_postgres_password_here/$POSTGRES_PASSWORD/g" .env
sed -i "s/your_secret_key_for_jwt_here/$SECRET_KEY/g" .env
sed -i "s/your_jwt_secret_here/$JWT_SECRET/g" .env

# Создание systemd сервиса
echo "⚙️ Создание systemd сервиса..."
cat > /etc/systemd/system/express-bot.service << EOF
[Unit]
Description=Express.ms Bot Production
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/express/bots/production
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
systemctl daemon-reload

# Создание скрипта мониторинга
echo "📊 Создание скрипта мониторинга..."
cat > /opt/express/bots/production/monitor.sh << 'EOF'
#!/bin/bash

echo "📊 Express.ms Bot Production Monitor"
echo "===================================="

# Проверка статуса контейнеров
echo "🐳 Статус контейнеров:"
docker-compose ps

echo ""
echo "💾 Использование ресурсов:"
docker stats --no-stream

echo ""
echo "🔍 Логи (последние 10 строк):"
docker-compose logs --tail=10

echo ""
echo "🏥 Health check:"
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "❌ Health check не прошел"

echo ""
echo "📈 Статистика бота:"
curl -s http://localhost:8000/stats | jq . 2>/dev/null || echo "❌ Stats недоступны"
EOF

chmod +x /opt/express/bots/production/monitor.sh

# Создание скрипта резервного копирования
echo "💾 Создание скрипта резервного копирования..."
cat > /opt/express/bots/production/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/express/bots/production/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Создание резервной копии..."

# Резервное копирование базы данных
docker exec express-bot-postgres-prod pg_dump -U express_bot_user express_bot_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# Резервное копирование Redis
docker exec express-bot-redis-prod redis-cli --rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

# Сжатие резервных копий
cd "$BACKUP_DIR"
tar -czf "backup_$DATE.tar.gz" "db_backup_$DATE.sql" "redis_backup_$DATE.rdb"
rm "db_backup_$DATE.sql" "redis_backup_$DATE.rdb"

echo "✅ Резервная копия создана: backup_$DATE.tar.gz"

# Удаление старых резервных копий (старше 30 дней)
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete

echo "🧹 Старые резервные копии удалены"
EOF

chmod +x /opt/express/bots/production/backup.sh

# Настройка cron для резервного копирования
echo "⏰ Настройка cron для резервного копирования..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/express/bots/production/backup.sh") | crontab -

# Создание скрипта обновления
echo "🔄 Создание скрипта обновления..."
cat > /opt/express/bots/production/update.sh << 'EOF'
#!/bin/bash

echo "🔄 Обновление Express.ms Bot..."

# Создание резервной копии
./backup.sh

# Остановка сервиса
docker-compose down

# Обновление образов
docker-compose pull

# Пересборка и запуск
docker-compose up --build -d

# Проверка статуса
sleep 10
docker-compose ps

echo "✅ Обновление завершено"
EOF

chmod +x /opt/express/bots/production/update.sh

echo "✅ Production развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте /opt/express/bots/production/.env"
echo "2. Укажите правильные BOT_CREDENTIALS и HOST"
echo "3. Настройте домен в .env файле"
echo "4. Запустите бота: systemctl start express-bot"
echo "5. Включите автозапуск: systemctl enable express-bot"
echo ""
echo "🌐 После запуска бот будет доступен на:"
echo "   - HTTP: http://localhost (редирект на HTTPS)"
echo "   - HTTPS: https://localhost"
echo "   - Health: https://localhost/health"
echo "   - Webhook: https://localhost/webhook"
echo ""
echo "📊 Мониторинг:"
echo "   - Статус: systemctl status express-bot"
echo "   - Логи: journalctl -u express-bot -f"
echo "   - Мониторинг: /opt/express/bots/production/monitor.sh"
echo ""
echo "💾 Резервное копирование:"
echo "   - Ручное: /opt/express/bots/production/backup.sh"
echo "   - Автоматическое: каждый день в 2:00"
echo ""
echo "🔄 Обновление:"
echo "   - /opt/express/bots/production/update.sh"
echo ""
echo "📞 Для получения BOT_CREDENTIALS обратитесь к разработчикам Express.ms"
