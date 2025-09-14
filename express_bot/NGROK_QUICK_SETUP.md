# 🚀 Быстрая настройка ngrok для Express Bot

## 📋 Шаги установки:

### 1. Остановите Cloudflare:
```bash
pkill cloudflared
```

### 2. Установите unzip и ngrok:
```bash
# Установите unzip
apt update && apt install -y unzip

# Скачайте ngrok
wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip

# Распакуйте ngrok
unzip /tmp/ngrok.zip -d /usr/local/bin/

# Сделайте исполняемым
chmod +x /usr/local/bin/ngrok
```

### 3. Запустите ngrok:
```bash
# В новом терминале
ngrok http 5010
```

### 4. Получите URL туннеля:
После запуска вы увидите:
```
Session Status                online
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5010
```

**Ваш URL**: `https://abc123.ngrok.io`

### 5. Обновите конфигурацию:
```bash
# Отредактируйте config.json
nano /root/test/express_bot/config.json

# Замените webhook_url на:
"webhook_url": "https://abc123.ngrok.io/webhook"
```

### 6. Настройте в Express.ms:
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Добавьте новое приложение:
   - **Название**: Flight Booking Bot
   - **URL приложения**: `https://abc123.ngrok.io`
   - **Webhook URL**: `https://abc123.ngrok.io/webhook`
   - **Иконка**: ✈️

## 🧪 Тестирование:
```bash
# Health check
curl https://abc123.ngrok.io/health

# Webhook test
curl -X POST https://abc123.ngrok.io/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

## 📊 Мониторинг:
- **Админ панель**: `https://abc123.ngrok.io/admin`
- **ngrok веб-интерфейс**: http://localhost:4040
- **Статистика**: `https://abc123.ngrok.io/api/stats`

## 🔧 Управление:
```bash
# Остановить туннель
pkill ngrok

# Запустить туннель
ngrok http 5010

# Проверить статус
curl http://localhost:4040/api/tunnels
```

## ✅ Преимущества ngrok:
- 🔒 **Стабильный** - намного надежнее Cloudflare
- 🚀 **Быстрый** - мгновенный запуск
- 📊 **Веб-интерфейс** - мониторинг на http://localhost:4040
- 🔧 **Простое управление** - легко запускать/останавливать
- 🌐 **Постоянный URL** - не меняется при перезапуске (с аккаунтом)

## 🎯 Ожидаемый результат:
После настройки бот должен:
- Показывать статус "онлайн" в Express.ms
- Отвечать на команду `/start`
- Позволять подавать заявки на рейсы
- Отображать статистику в админ панели


