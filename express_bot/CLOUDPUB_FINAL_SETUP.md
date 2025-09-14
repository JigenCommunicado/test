# 🚀 Express Bot с CloudPub - Финальная настройка

## ✅ Статус: Готов к использованию!

Ваш Express Bot успешно адаптирован для работы с CloudPub - российской альтернативой для туннелирования.

## 📋 Информация о боте:

- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **CloudPub URL**: `https://loosely-welcoming-grackle.cloudpub.ru`
- **Webhook URL**: `https://loosely-welcoming-grackle.cloudpub.ru/webhook`
- **Admin Panel**: `https://loosely-welcoming-grackle.cloudpub.ru/admin`
- **Статус CloudPub**: ✅ Активен

## 🔧 Быстрый запуск:

### 1. Запуск бота:
```bash
cd /root/test/express_bot
./start_cloudpub_bot.sh
```

### 2. Остановка бота:
```bash
cd /root/test/express_bot
./stop_cloudpub_bot.sh
```

### 3. Проверка статуса:
```bash
# Проверка CloudPub
sudo clo ls

# Проверка бота
ps aux | grep express_bot_cloudpub

# Проверка порта
lsof -i :5011
```

## 🧪 Тестирование:

### Health Check:
```bash
curl https://loosely-welcoming-grackle.cloudpub.ru/health
```

### Manifest:
```bash
curl https://loosely-welcoming-grackle.cloudpub.ru/manifest
```

### Webhook Test:
```bash
curl -X POST https://loosely-welcoming-grackle.cloudpub.ru/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

### Admin Panel:
Откройте в браузере: https://loosely-welcoming-grackle.cloudpub.ru/admin

## 📱 Настройка в Express.ms:

### 1. Добавьте бота как SmartApp:
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Нажмите "Добавить новое приложение"
4. Заполните поля:
   - **Название**: Flight Booking Bot
   - **Описание**: Бот для подачи заявок на командировочные рейсы
   - **URL приложения**: `https://loosely-welcoming-grackle.cloudpub.ru`
   - **Webhook URL**: `https://loosely-welcoming-grackle.cloudpub.ru/webhook`
   - **Иконка**: ✈️
   - **Цвет**: #0088cc

### 2. Настройте webhook:
- **Webhook URL**: `https://loosely-welcoming-grackle.cloudpub.ru/webhook`
- **События**: message, command, callback_query
- **Метод**: POST
- **Content-Type**: application/json

## 🔧 Управление CloudPub:

### Просмотр сервисов:
```bash
sudo clo ls
```

### Остановка сервиса:
```bash
sudo clo stop express-bot
```

### Запуск сервиса:
```bash
sudo clo start express-bot
```

### Удаление сервиса:
```bash
sudo clo remove express-bot
```

### Перезапуск сервиса:
```bash
sudo systemctl restart clo.service
```

### Просмотр логов:
```bash
# Логи CloudPub
sudo journalctl -u clo.service -f

# Логи бота
tail -f /root/test/express_bot/cloudpub_bot.log
```

## ✅ Преимущества CloudPub:

- 🇷🇺 **Российский сервис** - быстрый доступ из России
- 🔒 **Безопасный** - защищенное соединение
- 🚀 **Стабильный** - надежная работа
- 🔧 **Простой** - легкая настройка
- 🌐 **Постоянный URL** - не меняется при перезапуске
- 💰 **Бесплатный** - для базового использования

## 🎯 Ожидаемый результат:

После настройки в Express.ms бот должен:
- ✅ Показывать статус "онлайн"
- ✅ Отвечать на команду `/start`
- ✅ Позволять подавать заявки на рейсы
- ✅ Отображать статистику в админ панели

## 🔧 Устранение проблем:

### Бот не отвечает:
```bash
# Проверьте статус CloudPub
sudo clo ls

# Проверьте, что бот запущен
ps aux | grep express_bot_cloudpub

# Перезапустите бота
./stop_cloudpub_bot.sh
./start_cloudpub_bot.sh
```

### Webhook не работает:
```bash
# Проверьте URL
curl https://loosely-welcoming-grackle.cloudpub.ru/health

# Проверьте webhook
curl -X POST https://loosely-welcoming-grackle.cloudpub.ru/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

### CloudPub не работает:
```bash
# Проверьте статус
sudo systemctl status clo.service

# Перезапустите
sudo systemctl restart clo.service

# Проверьте логи
sudo journalctl -u clo.service -f
```

## 📊 Мониторинг:

- **Админ панель**: https://loosely-welcoming-grackle.cloudpub.ru/admin
- **Статистика API**: https://loosely-welcoming-grackle.cloudpub.ru/api/stats
- **Логи бота**: `/root/test/express_bot/cloudpub_bot.log`
- **Логи CloudPub**: `sudo journalctl -u clo.service -f`

## 🚀 Готово к использованию!

Ваш Express Bot успешно адаптирован для работы с CloudPub и готов к интеграции с Express.ms! 🎉

**Основные файлы:**
- `express_bot_cloudpub.py` - основной файл бота
- `start_cloudpub_bot.sh` - скрипт запуска
- `stop_cloudpub_bot.sh` - скрипт остановки
- `config.json` - конфигурация с CloudPub URL

**Следующие шаги:**
1. Запустите бота: `./start_cloudpub_bot.sh`
2. Настройте в Express.ms
3. Протестируйте команду `/start`
4. Наслаждайтесь стабильной работой! 🎉
