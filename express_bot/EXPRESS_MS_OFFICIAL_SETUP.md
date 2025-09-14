# 🏢 Официальное развертывание Express.ms Bot

## 📋 Согласно руководству администратора Express.ms

### 🔑 **Требования:**
- **Docker** + **Docker Compose**
- **PostgreSQL v15** + **Redis v7**
- **Доступ к registry.public.express**
- **Login/Password** от разработчиков Express.ms

### 🏗️ **Архитектура:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Express.ms    │◄──►│   Bot Server     │◄──►│   PostgreSQL    │
│   (CTS)         │    │   (Docker)       │    │   + Redis       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 📝 **Шаги развертывания:**

#### 1️⃣ **Регистрация в панели администратора CTS**
- Перейти в раздел "Боты"
- Нажать "Создать бота"
- Заполнить поля:
  - **URL**: `https://<bot-server>:8000`
  - **ID** и **Secret key** - сохранить!

#### 2️⃣ **Подготовка сервера**
```bash
# Создание директорий
mkdir -p /opt/express/bots/storages
mkdir -p /opt/express/bots/your_bot

# Копирование файлов от разработчиков:
# - docker-compose.storages.yml
# - docker-compose.yml  
# - .env
```

#### 3️⃣ **Настройка общего хранилища**
```bash
cd /opt/express/bots/storages

# Создание .env для хранилища
cat > .env << EOF
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="$(openssl rand -hex 32)"
EOF

# Запуск PostgreSQL + Redis
docker compose -f docker-compose.storages.yml up -d
```

#### 4️⃣ **Создание базы данных для бота**
```bash
# Создание пользователя и БД
docker exec storages-postgres-1 psql -U postgres -c "create user 'your_bot_user'"
docker exec storages-postgres-1 psql -U postgres -c "alter user 'your_bot_user' with password '$(openssl rand -hex 32)'"
docker exec storages-postgres-1 psql -U postgres -c "create database 'your_bot_db' with owner 'your_bot_user'"
```

#### 5️⃣ **Настройка бота**
```bash
cd /opt/express/bots/your_bot

# Создание .env для бота
cat > .env << EOF
BOT_CREDENTIALS="<bot_id>:<secret_key>"
HOST="<cts_host>"
DATABASE_URL="postgresql://your_bot_user:<password>@storages-postgres-1:5432/your_bot_db"
REDIS_URL="redis://storages-redis-1:6379"
EOF
```

#### 6️⃣ **Авторизация в Docker Registry**
```bash
docker login -u <Login> -p <Password> registry.public.express
```

#### 7️⃣ **Запуск бота**
```bash
docker compose up -d
```

### 🔍 **Проверка работоспособности:**
```bash
# Проверка статуса
docker compose ps

# Проверка логов
docker compose logs

# Проверка подключения к CTS
curl https://<bot-server>:8000/health
```

### 📞 **Получение доступа:**
- **Панель администратора CTS**: Обратиться к разработчикам Express.ms
- **Docker Registry**: Получить Login/Password
- **Техподдержка**: support@express.ms

### ⚠️ **Важно:**
- Наш текущий Python-бот **НЕ совместим** с официальной архитектурой
- Нужны **официальные Docker-образы** из registry.public.express
- Требуется **доступ к панели администратора CTS**

### 🎯 **Следующие шаги:**
1. Связаться с разработчиками Express.ms
2. Получить доступ к панели администратора
3. Получить Login/Password для Docker Registry
4. Получить официальные файлы развертывания
5. Развернуть бота согласно официальной документации
