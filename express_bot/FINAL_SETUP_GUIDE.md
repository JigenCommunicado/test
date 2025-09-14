# 🚀 Express Bot - Финальная настройка

## 📋 Информация о боте:
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Secret Key**: `a75b4cd97d9e88e543f077178b2d5a4f`
- **Порт**: `5010`
- **Admin Panel**: `http://localhost:5010/admin`

## 🌐 Варианты туннелей:

### 1. LocalTunnel (Рекомендуется)
```bash
# Запуск
npx localtunnel --port 5010 --subdomain express-bot-flight

# Webhook URL
https://express-bot-flight.loca.lt/webhook
```

### 2. Cloudflare Tunnel
```bash
# Запуск
cloudflared tunnel --url http://localhost:5010

# Webhook URL (меняется каждый раз)
https://[random-name].trycloudflare.com/webhook
```

### 3. ngrok (требует регистрации)
```bash
# Установка
wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
unzip /tmp/ngrok.zip -d /usr/local/bin/
chmod +x /usr/local/bin/ngrok

# Настройка (требует токен)
ngrok config add-authtoken YOUR_TOKEN

# Запуск
ngrok http 5010
```

## 🔧 Быстрый запуск:

### Вариант 1: LocalTunnel
```bash
cd /root/test/express_bot
chmod +x start_with_localtunnel.sh
./start_with_localtunnel.sh
```

### Вариант 2: Ручной запуск
```bash
# 1. Запускаем бот
cd /root/test/express_bot
python3 express_bot_with_admin.py &

# 2. Запускаем туннель
npx localtunnel --port 5010 --subdomain express-bot-flight &

# 3. Проверяем статус
ps aux | grep -E "(express_bot_with_admin|localtunnel)" | grep -v grep
```

## 📱 Настройка в Express.ms:

### 1. Добавьте бота как SmartApp:
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Нажмите "Добавить новое приложение"
4. Заполните поля:
   - **Название**: Flight Booking Bot
   - **Описание**: Бот для подачи заявок на командировочные рейсы
   - **URL приложения**: `https://express-bot-flight.loca.lt`
   - **Webhook URL**: `https://express-bot-flight.loca.lt/webhook`
   - **Иконка**: ✈️
   - **Цвет**: #0088cc

### 2. Настройте webhook:
- **Webhook URL**: `https://express-bot-flight.loca.lt/webhook`
- **События**: message, command, callback_query
- **Метод**: POST
- **Content-Type**: application/json

## 🧪 Тестирование:

### 1. Проверка бота:
```bash
# Health check
curl http://localhost:5010/health

# Manifest
curl http://localhost:5010/manifest

# Admin panel
curl http://localhost:5010/admin
```

### 2. Проверка туннеля:
```bash
# Health check через туннель
curl https://express-bot-flight.loca.lt/health

# Webhook test
curl -X POST https://express-bot-flight.loca.lt/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

### 3. Тестирование в Express.ms:
1. Отправьте команду `/start` боту
2. Проверьте админ панель: `https://express-bot-flight.loca.lt/admin`
3. Проверьте статистику: `https://express-bot-flight.loca.lt/api/stats`

## 📊 Мониторинг:

### Логи бота:
```bash
tail -f /root/test/express_bot/fixed_bot.log
```

### Статус процессов:
```bash
ps aux | grep -E "(express_bot_with_admin|localtunnel)" | grep -v grep
```

### Проверка портов:
```bash
netstat -tlnp | grep 5010
```

## 🔧 Устранение проблем:

### 1. Бот не запускается:
```bash
# Проверьте порт
netstat -tlnp | grep 5010

# Если занят, убейте процесс
sudo kill -9 $(lsof -t -i:5010)

# Запустите заново
python3 express_bot_with_admin.py
```

### 2. Туннель не работает:
```bash
# Остановите все туннели
pkill -f localtunnel
pkill -f cloudflared
pkill -f ngrok

# Запустите заново
npx localtunnel --port 5010 --subdomain express-bot-flight
```

### 3. Webhook не отвечает:
- Проверьте, что бот запущен
- Проверьте, что туннель работает
- Проверьте URL в Express.ms
- Проверьте логи бота

## 🎯 Ожидаемый результат:

После настройки бот должен:
- ✅ Показывать статус "онлайн" в Express.ms
- ✅ Отвечать на команду `/start`
- ✅ Позволять подавать заявки на рейсы
- ✅ Отображать статистику в админ панели
- ✅ Обрабатывать webhook события

## 📞 Поддержка:

- **Логи бота**: `/root/test/express_bot/fixed_bot.log`
- **Конфигурация**: `/root/test/express_bot/config.json`
- **Админ панель**: `https://express-bot-flight.loca.lt/admin`
- **Документация Express.ms**: https://docs.express.ms/smartapps

## 🚀 Готово к использованию!

Ваш бот настроен и готов к работе с Express.ms. Используйте LocalTunnel для стабильной работы или любой другой туннель по вашему выбору.

