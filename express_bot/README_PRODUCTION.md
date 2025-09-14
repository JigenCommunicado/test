# 🚀 Express.ms Bot Production Deployment

## 📋 Production развертывание согласно официальной документации Express.ms

### 🏗️ **Production архитектура:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Express.ms    │◄──►│   Nginx (SSL)    │◄──►│   Bot Server    │
│   (CTS)         │    │   (Load Balancer)│    │   (Docker)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   PostgreSQL    │
                                               │   + Redis       │
                                               └─────────────────┘
```

### 🚀 **Быстрый запуск Production:**

#### 1️⃣ **Автоматическое развертывание:**
```bash
sudo chmod +x deploy_production.sh
sudo ./deploy_production.sh
```

#### 2️⃣ **Ручное развертывание:**
```bash
# Создание директорий
sudo mkdir -p /opt/express/bots/production
cd /opt/express/bots/production

# Копирование файлов
cp docker-compose.prod.yml docker-compose.yml
cp Dockerfile.prod Dockerfile
cp requirements.txt .
cp express_bot_docker.py .
cp init.sql .
cp nginx.conf .
cp postgresql.conf .
cp redis.conf .
cp env.prod .env

# Настройка SSL
chmod +x setup_ssl.sh
./setup_ssl.sh

# Редактирование конфигурации
nano .env

# Запуск
docker-compose up --build -d
```

### 🔧 **Управление Production сервисом:**

#### **Systemd сервис:**
```bash
# Запуск
sudo systemctl start express-bot

# Остановка
sudo systemctl stop express-bot

# Перезапуск
sudo systemctl restart express-bot

# Статус
sudo systemctl status express-bot

# Включение автозапуска
sudo systemctl enable express-bot

# Логи
journalctl -u express-bot -f
```

#### **Docker Compose:**
```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Логи
docker-compose logs -f

# Обновление
docker-compose pull
docker-compose up --build -d
```

### 🌐 **Production Endpoints:**

- **HTTPS**: `https://your-domain.com`
- **Health Check**: `https://your-domain.com/health`
- **Manifest**: `https://your-domain.com/manifest`
- **Stats**: `https://your-domain.com/stats`
- **Webhook**: `https://your-domain.com/webhook`
- **Admin Panel**: `https://your-domain.com/admin`

### 📊 **Мониторинг и управление:**

#### **Скрипт мониторинга:**
```bash
/opt/express/bots/production/monitor.sh
```

#### **Резервное копирование:**
```bash
# Ручное
/opt/express/bots/production/backup.sh

# Автоматическое (cron)
# Каждый день в 2:00
```

#### **Обновление:**
```bash
/opt/express/bots/production/update.sh
```

### 🔐 **Безопасность:**

#### **SSL/TLS:**
- Самоподписанный сертификат для тестирования
- Let's Encrypt для production
- Автоматическое обновление сертификатов

#### **Firewall:**
```bash
# Открытие портов
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# Закрытие внутренних портов
sudo ufw deny 5432/tcp
sudo ufw deny 6379/tcp
sudo ufw deny 8000/tcp
```

#### **Rate Limiting:**
- API: 100 запросов/час
- Webhook: 5 запросов/секунду
- Burst: 20 запросов

### 📈 **Производительность:**

#### **Ресурсы:**
- **Bot**: 512MB RAM, 0.5 CPU
- **PostgreSQL**: 1GB RAM, 1.0 CPU
- **Redis**: 512MB RAM, 0.5 CPU
- **Nginx**: 128MB RAM, 0.25 CPU

#### **Оптимизация:**
- Connection pooling
- Query optimization
- Caching strategies
- Gzip compression

### 🚨 **Устранение неполадок:**

#### **Проверка статуса:**
```bash
# Статус сервиса
sudo systemctl status express-bot

# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Логи
docker-compose logs -f
```

#### **Проблемы с SSL:**
```bash
# Проверка сертификата
openssl x509 -in ssl/cert.pem -text -noout

# Проверка подключения
curl -k https://localhost/health
```

#### **Проблемы с базой данных:**
```bash
# Подключение к PostgreSQL
docker exec -it express-bot-postgres-prod psql -U express_bot_user -d express_bot_db

# Проверка Redis
docker exec -it express-bot-redis-prod redis-cli ping

# Проверка логов БД
docker-compose logs postgres
```

#### **Проблемы с сетью:**
```bash
# Проверка сети
docker network ls
docker network inspect express-bot_express-network

# Проверка портов
netstat -tlnp | grep -E "(80|443|8000)"
```

### 📋 **Конфигурация:**

#### **Основные настройки (.env):**
```bash
# Bot Credentials
BOT_CREDENTIALS=bot_id:secret_key

# Express.ms Host
HOST=https://api.express.ms

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/db

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# Domain
DOMAIN=your-domain.com
WEBHOOK_URL=https://your-domain.com/webhook
```

#### **Nginx настройки:**
- SSL/TLS termination
- Load balancing
- Rate limiting
- Security headers
- Gzip compression

#### **PostgreSQL настройки:**
- Connection pooling
- Query optimization
- Logging
- Backup configuration

#### **Redis настройки:**
- Memory optimization
- Persistence
- Security
- Monitoring

### 🔄 **Обновление и обслуживание:**

#### **Обновление бота:**
```bash
# Автоматическое
/opt/express/bots/production/update.sh

# Ручное
docker-compose down
docker-compose pull
docker-compose up --build -d
```

#### **Обновление системы:**
```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Перезапуск сервисов
sudo systemctl restart express-bot
```

#### **Мониторинг:**
- Health checks
- Resource usage
- Error rates
- Response times
- Database performance

### 📞 **Поддержка:**

- **Express.ms Support**: support@express.ms
- **Документация**: https://express.ms/faq/
- **Sales**: sales@express.ms

### ⚠️ **Важные замечания:**

1. **Получите доступ к панели администратора Express.ms**
2. **Настройте правильный домен и SSL сертификат**
3. **Настройте мониторинг и алерты**
4. **Регулярно создавайте резервные копии**
5. **Обновляйте систему и зависимости**
6. **Мониторьте производительность и логи**

### 🎯 **Production Checklist:**

- [ ] Получен доступ к панели администратора Express.ms
- [ ] Настроены BOT_CREDENTIALS
- [ ] Настроен домен и SSL сертификат
- [ ] Настроен firewall
- [ ] Настроен мониторинг
- [ ] Настроено резервное копирование
- [ ] Протестированы все endpoints
- [ ] Настроены алерты
- [ ] Документированы процедуры
- [ ] Обучен персонал
