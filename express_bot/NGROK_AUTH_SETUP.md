# 🔐 Настройка ngrok с аутентификацией для Express Bot

## ❌ Проблема
ngrok требует аутентификации для работы. Ошибка:
```
ERROR: authentication failed: Usage of ngrok requires a verified account and authtoken.
```

## ✅ Решение

### 1. Получите ngrok authtoken

1. Перейдите на https://dashboard.ngrok.com/signup
2. Зарегистрируйтесь или войдите в аккаунт
3. Перейдите на https://dashboard.ngrok.com/get-started/your-authtoken
4. Скопируйте ваш authtoken

### 2. Настройте ngrok

#### Вариант A: Автоматическая настройка
```bash
cd /root/test/express_bot
chmod +x setup_ngrok_auth.sh
./setup_ngrok_auth.sh
```

#### Вариант B: Ручная настройка
```bash
# Установите authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE

# Запустите туннель
ngrok http 8000
```

#### Вариант C: Простой запуск
```bash
cd /root/test/express_bot
chmod +x start_ngrok_simple.sh
./start_ngrok_simple.sh
```

### 3. Получите URL туннеля

После запуска ngrok:
1. Откройте http://localhost:4040 в браузере
2. Скопируйте URL туннеля (например: https://abc123.ngrok.io)
3. Ваш webhook URL будет: `https://abc123.ngrok.io/webhook`

## 🐳 Запуск с Docker

После настройки ngrok authtoken:

```bash
cd /root/test/express_bot

# Обновите ngrok.yml с вашим authtoken
cat > ngrok.yml << EOF
version: "2"
authtoken: YOUR_AUTHTOKEN_HERE
tunnels:
  express-bot:
    proto: http
    addr: express-bot:8000
    inspect: true
    bind_tls: true
    web_addr: 0.0.0.0:4040
EOF

# Запустите Docker сервисы
export POSTGRES_PASSWORD=express_bot_password
export POSTGRES_DB=express_bot_db
export POSTGRES_USER=express_bot_user
export BOT_CREDENTIALS=00c46d64-1127-5a96-812d-3d8b27c58b99:a75b4cd97d9e88e543f077178b2d5a4f
export HOST=https://api.express.ms
export DATABASE_URL=postgresql://express_bot_user:express_bot_password@postgres:5432/express_bot_db
export REDIS_URL=redis://redis:6379/0
export LOG_LEVEL=INFO

docker-compose -f docker-compose.ngrok.yml up -d
```

## 🧪 Тестирование

### 1. Проверьте ngrok
```bash
curl http://localhost:4040/api/tunnels
```

### 2. Проверьте бота
```bash
curl http://localhost:8000/health
```

### 3. Тестируйте webhook
```bash
curl -X POST https://YOUR_NGROK_URL.ngrok.io/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

## 🔧 Настройка в Express.ms

1. Откройте админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Добавьте новое приложение:
   - **Название**: Express Bot
   - **URL приложения**: `https://YOUR_NGROK_URL.ngrok.io`
   - **Webhook URL**: `https://YOUR_NGROK_URL.ngrok.io/webhook`
   - **Описание**: Бот для Express.ms

## 📊 Мониторинг

- **ngrok веб-интерфейс**: http://localhost:4040
- **Bot health**: http://localhost:8000/health
- **Bot stats**: http://localhost:8000/stats

## 🔧 Устранение проблем

1. **Ошибка аутентификации**: Проверьте правильность authtoken
2. **Туннель не создается**: Проверьте, что порт 8000 свободен
3. **Webhook не работает**: Проверьте URL в Express.ms

## 📞 Поддержка

- ngrok документация: https://ngrok.com/docs
- ngrok dashboard: https://dashboard.ngrok.com
- Логи ngrok: http://localhost:4040
