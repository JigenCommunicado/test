# 🚀 Пошаговое руководство Express.ms Bot

## 📋 Полная настройка согласно официальной документации

### 🎯 **Автоматическая настройка (рекомендуется):**

```bash
# Запуск полной автоматической настройки
sudo chmod +x setup_complete.sh
sudo ./setup_complete.sh bot.yourcompany.com admin@yourcompany.com
```

### 📋 **Ручная настройка по шагам:**

#### **ШАГ 1: Проверка системы**
```bash
# Проверка Docker
docker --version
docker-compose --version

# Установка если нужно
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
```

#### **ШАГ 2: Создание структуры директорий**
```bash
# Создание директорий согласно документации Express.ms
sudo mkdir -p /opt/express/bots/storages
sudo mkdir -p /opt/express/bots/production
sudo mkdir -p /opt/express/bots/production/{logs,data,ssl,backups}
```

#### **ШАГ 3: Настройка общего хранилища**
```bash
cd /opt/express/bots/storages

# Копирование файлов
sudo cp /root/test/express_bot/docker-compose.storages.yml .

# Создание .env для хранилища
sudo tee .env << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(openssl rand -hex 32)
EOF

# Запуск PostgreSQL и Redis
sudo docker-compose -f docker-compose.storages.yml up -d
```

#### **ШАГ 4: Создание базы данных для бота**
```bash
# Генерация паролей
BOT_DB_PASSWORD=$(openssl rand -hex 32)

# Создание пользователя и БД
sudo docker exec storages-postgres-1 psql -U postgres -c "CREATE USER express_bot_user;"
sudo docker exec storages-postgres-1 psql -U postgres -c "ALTER USER express_bot_user WITH PASSWORD '$BOT_DB_PASSWORD';"
sudo docker exec storages-postgres-1 psql -U postgres -c "CREATE DATABASE express_bot_db WITH OWNER express_bot_user;"
```

#### **ШАГ 5: Настройка production бота**
```bash
cd /opt/express/bots/production

# Копирование файлов
sudo cp /root/test/express_bot/docker-compose.prod.yml docker-compose.yml
sudo cp /root/test/express_bot/Dockerfile.prod Dockerfile
sudo cp /root/test/express_bot/requirements.txt .
sudo cp /root/test/express_bot/express_bot_docker.py .
sudo cp /root/test/express_bot/init.sql .
sudo cp /root/test/express_bot/nginx.conf .
sudo cp /root/test/express_bot/postgresql.conf .
sudo cp /root/test/express_bot/redis.conf .
sudo cp /root/test/express_bot/env.prod .env

# Обновление .env файла
sudo sed -i "s/your_secure_postgres_password_here/$BOT_DB_PASSWORD/g" .env
sudo sed -i "s/your-domain.com/bot.yourcompany.com/g" .env
```

#### **ШАГ 6: Настройка SSL сертификата**

**Вариант A: Let's Encrypt (рекомендуется)**
```bash
# Установка certbot
sudo apt install certbot

# Остановка nginx
sudo systemctl stop nginx

# Получение сертификата
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@yourcompany.com \
    --domains bot.yourcompany.com

# Копирование сертификатов
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/bot.yourcompany.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/bot.yourcompany.com/privkey.pem ssl/key.pem
sudo chmod 644 ssl/cert.pem
sudo chmod 600 ssl/key.pem
```

**Вариант B: Самоподписанный (для тестирования)**
```bash
# Создание самоподписанного сертификата
sudo mkdir -p ssl
sudo openssl genrsa -out ssl/key.pem 2048
sudo openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Express.ms Bot/OU=IT Department/CN=bot.yourcompany.com"
sudo chmod 600 ssl/key.pem
sudo chmod 644 ssl/cert.pem
```

#### **ШАГ 7: Настройка Firewall**
```bash
# Установка ufw
sudo apt install ufw

# Настройка правил
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw deny 5432/tcp comment 'PostgreSQL (внутренний)'
sudo ufw deny 6379/tcp comment 'Redis (внутренний)'
sudo ufw deny 8000/tcp comment 'Bot Server (внутренний)'
sudo ufw logging on
sudo ufw --force enable
```

#### **ШАГ 8: Создание systemd сервиса**
```bash
# Создание сервиса
sudo tee /etc/systemd/system/express-bot.service << EOF
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

# Включение сервиса
sudo systemctl daemon-reload
sudo systemctl enable express-bot
```

#### **ШАГ 9: Запуск бота**
```bash
cd /opt/express/bots/production

# Запуск бота
sudo docker-compose up --build -d

# Проверка статуса
sudo docker-compose ps
```

#### **ШАГ 10: Проверка работоспособности**
```bash
# Проверка health check
curl -k https://bot.yourcompany.com/health

# Проверка webhook
curl -k -X POST https://bot.yourcompany.com/webhook \
    -H "Content-Type: application/json" \
    -d '{"type": "message", "user_id": "test", "text": "/start"}'

# Проверка логов
sudo docker-compose logs -f
```

### 🔧 **Управление ботом:**

#### **Systemd сервис:**
```bash
# Статус
sudo systemctl status express-bot

# Запуск
sudo systemctl start express-bot

# Остановка
sudo systemctl stop express-bot

# Перезапуск
sudo systemctl restart express-bot

# Логи
journalctl -u express-bot -f
```

#### **Docker Compose:**
```bash
cd /opt/express/bots/production

# Статус
sudo docker-compose ps

# Логи
sudo docker-compose logs -f

# Перезапуск
sudo docker-compose restart

# Остановка
sudo docker-compose down

# Обновление
sudo docker-compose pull
sudo docker-compose up --build -d
```

### 📊 **Мониторинг:**

#### **Скрипт мониторинга:**
```bash
cd /opt/express/bots/production
./monitor.sh
```

#### **Проверка ресурсов:**
```bash
# Использование ресурсов
sudo docker stats

# Проверка портов
sudo netstat -tlnp | grep -E "(80|443|8000)"

# Проверка дискового пространства
df -h
```

### 💾 **Резервное копирование:**

#### **Автоматическое (cron):**
```bash
# Резервное копирование каждый день в 2:00
0 2 * * * /opt/express/bots/production/backup.sh
```

#### **Ручное:**
```bash
cd /opt/express/bots/production
./backup.sh
```

### 🚨 **Устранение неполадок:**

#### **Проблемы с Docker:**
```bash
# Перезапуск Docker
sudo systemctl restart docker

# Очистка контейнеров
sudo docker system prune -a

# Проверка логов Docker
sudo journalctl -u docker -f
```

#### **Проблемы с SSL:**
```bash
# Проверка сертификата
openssl x509 -in ssl/cert.pem -text -noout

# Проверка подключения
openssl s_client -connect bot.yourcompany.com:443 -servername bot.yourcompany.com
```

#### **Проблемы с базой данных:**
```bash
# Подключение к PostgreSQL
sudo docker exec -it express-bot-postgres-prod psql -U express_bot_user -d express_bot_db

# Проверка Redis
sudo docker exec -it express-bot-redis-prod redis-cli ping
```

### 📋 **Checklist для настройки:**

- [ ] Docker и Docker Compose установлены
- [ ] Директории созданы
- [ ] Общее хранилище настроено
- [ ] База данных для бота создана
- [ ] Production конфигурация готова
- [ ] SSL сертификат настроен
- [ ] Firewall настроен
- [ ] Systemd сервис создан
- [ ] Бот запущен и работает
- [ ] Health check проходит
- [ ] Webhook доступен
- [ ] Мониторинг настроен
- [ ] Резервное копирование настроено

### 📞 **Поддержка Express.ms:**

- **Sales**: sales@express.ms
- **Support**: support@express.ms
- **Документация**: https://express.ms/faq/
- **Панель администратора**: Обратиться к разработчикам

### ⚠️ **Важные замечания:**

1. **Получите BOT_CREDENTIALS** от разработчиков Express.ms
2. **Настройте DNS** для вашего домена
3. **Используйте Let's Encrypt** для production
4. **Мониторьте ресурсы** и логи
5. **Создавайте резервные копии** регулярно
6. **Обновляйте систему** и зависимости
