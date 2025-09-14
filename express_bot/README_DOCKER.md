
# 🐳 Express.ms Bot Docker Deployment

## 📋 Согласно официальной документации Express.ms

### 🏗️ **Архитектура:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Express.ms    │◄──►│   Bot Server     │◄──►│   PostgreSQL    │
│   (CTS)         │    │   (Docker)       │    │   + Redis       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🚀 **Быстрый старт:**

#### 1️⃣ **Автоматическая настройка:**
```bash
chmod +x setup_docker_bot.sh
./setup_docker_bot.sh
```

#### 2️⃣ **Ручная настройка:**
```bash
# Создание директорий
mkdir -p /opt/express/bots/storages
mkdir -p /opt/express/bots/express-bot

# Копирование файлов
cp docker-compose.storages.yml /opt/express/bots/storages/
cp docker-compose.yml /opt/express/bots/express-bot/
cp Dockerfile /opt/express/bots/express-bot/
cp requirements.txt /opt/express/bots/express-bot/
cp express_bot_docker.py /opt/express/bots/express-bot/
cp init.sql /opt/express/bots/express-bot/
cp env.example /opt/express/bots/express-bot/.env
```

#### 3️⃣ **Настройка хранилища:**
```bash
cd /opt/express/bots/storages

# Создание .env для хранилища
cat > .env << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(openssl rand -hex 32)
EOF

# Запуск PostgreSQL + Redis
docker-compose -f docker-compose.storages.yml up -d
```

#### 4️⃣ **Создание базы данных для бота:**
```bash
# Создание пользователя и БД
docker exec storages-postgres-1 psql -U postgres -c "CREATE USER express_bot_user;"
docker exec storages-postgres-1 psql -U postgres -c "ALTER USER express_bot_user WITH PASSWORD '$(openssl rand -hex 32)';"
docker exec storages-postgres-1 psql -U postgres -c "CREATE DATABASE express_bot_db WITH OWNER express_bot_user;"
```

#### 5️⃣ **Настройка бота:**
```bash
cd /opt/express/bots/express-bot

# Редактирование .env файла
nano .env

# Укажите правильные значения:
# BOT_CREDENTIALS=bot_id:secret_key
# HOST=https://api.express.ms
# DATABASE_URL=postgresql://express_bot_user:password@postgres:5432/express_bot_db
# REDIS_URL=redis://redis:6379
```

#### 6️⃣ **Запуск бота:**
```bash
# Автоматический запуск
chmod +x start_docker_bot.sh
./start_docker_bot.sh

# Или вручную
docker-compose up --build -d
```

### 🔧 **Управление:**

#### **Запуск:**
```bash
docker-compose up -d
```

#### **Остановка:**
```bash
docker-compose down
```

#### **Просмотр логов:**
```bash
docker-compose logs -f
```

#### **Перезапуск:**
```bash
docker-compose restart
```

### 🌐 **Endpoints:**

- **Health Check**: `http://localhost:8000/health`
- **Manifest**: `http://localhost:8000/manifest`
- **Stats**: `http://localhost:8000/stats`
- **Webhook**: `http://localhost:8000/webhook`

### 📊 **Мониторинг:**

#### **Статус контейнеров:**
```bash
docker-compose ps
```

#### **Использование ресурсов:**
```bash
docker stats
```

#### **Логи конкретного сервиса:**
```bash
docker-compose logs express-bot
docker-compose logs postgres
docker-compose logs redis
```

### 🔐 **Безопасность:**

#### **Генерация паролей:**
```bash
# PostgreSQL пароль
openssl rand -hex 32

# Redis пароль (если нужен)
openssl rand -hex 32
```

#### **Ограничение доступа:**
- Используйте firewall для ограничения доступа к портам
- Настройте SSL/TLS для production
- Регулярно обновляйте пароли

### 🚨 **Устранение неполадок:**

#### **Бот не запускается:**
```bash
# Проверка логов
docker-compose logs express-bot

# Проверка конфигурации
docker-compose config

# Пересборка
docker-compose up --build --force-recreate
```

#### **Проблемы с базой данных:**
```bash
# Проверка подключения к PostgreSQL
docker exec -it express-bot-postgres psql -U express_bot_user -d express_bot_db

# Проверка Redis
docker exec -it express-bot-redis redis-cli ping
```

#### **Проблемы с сетью:**
```bash
# Проверка сети
docker network ls
docker network inspect express-bot_express-network
```

### 📞 **Поддержка:**

- **Express.ms Support**: support@express.ms
- **Документация**: https://express.ms/faq/
- **Sales**: sales@express.ms

### ⚠️ **Важные замечания:**

1. **Получите доступ к панели администратора Express.ms** для регистрации бота
2. **Получите Login/Password для Docker Registry** `registry.public.express`
3. **Настройте правильные BOT_CREDENTIALS** в .env файле
4. **Убедитесь, что порт 8000 доступен** извне для webhook
5. **Используйте HTTPS в production** для безопасности

### 🎯 **Следующие шаги:**

1. Свяжитесь с разработчиками Express.ms
2. Получите доступ к панели администратора
3. Зарегистрируйте бота в CTS
4. Получите официальные Docker-образы
5. Настройте production развертывание
