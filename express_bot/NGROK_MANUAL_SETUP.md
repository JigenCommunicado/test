# 🚀 Настройка Express Bot с ngrok

## 📋 Преимущества ngrok:
- ✅ **Стабильный** - намного надежнее Cloudflare
- ✅ **Быстрый** - мгновенный запуск
- ✅ **Веб-интерфейс** - мониторинг на http://localhost:4040
- ✅ **Простое управление** - легко запускать/останавливать

## 🔧 Установка и настройка:

### 1. Установите ngrok:
```bash
cd /root/test/express_bot

# Скачиваем ngrok
wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip

# Распаковываем
unzip /tmp/ngrok.zip -d /usr/local/bin/

# Делаем исполняемым
chmod +x /usr/local/bin/ngrok
```

### 2. Запустите ngrok туннель:
```bash
# В новом терминале запустите:
ngrok http 5010
```

### 3. Получите URL туннеля:
После запуска вы увидите что-то вроде:
```
Session Status                online
Account                       (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5010
```

**Ваш URL**: `https://abc123.ngrok.io`

### 4. Обновите конфигурацию:
```bash
# Отредактируйте config.json
nano /root/test/express_bot/config.json

# Замените webhook_url на:
"webhook_url": "https://abc123.ngrok.io/webhook"
```

### 5. Настройте в Express.ms:
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

# Manifest
curl https://abc123.ngrok.io/manifest

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

## 🎯 Ожидаемый результат:
После настройки бот должен:
- Показывать статус "онлайн" в Express.ms
- Отвечать на команду `/start`
- Позволять подавать заявки на рейсы
- Отображать статистику в админ панели

## 🔧 Устранение проблем:
1. **Бот оффлайн**: Проверьте webhook URL и права доступа
2. **Ошибки webhook**: Проверьте логи бота
3. **Не отвечает**: Проверьте статус сервера и туннеля
4. **Туннель не работает**: Перезапустите ngrok

## 📞 Поддержка:
- Логи бота: `tail -f /root/test/express_bot/fixed_bot.log`
- Конфигурация: `/root/test/express_bot/config.json`
- Админ панель: `https://abc123.ngrok.io/admin`
- ngrok веб-интерфейс: http://localhost:4040


