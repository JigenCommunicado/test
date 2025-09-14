# 🚀 Ручная настройка Express Bot в Express.ms

## 📋 Текущий статус:
- **Бот запущен**: ✅ Порт 5010
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Статус**: Готов к настройке

## 🔧 Шаги настройки:

### 1. Создайте Cloudflare туннель
```bash
# В новом терминале запустите:
cd /root/test/express_bot
cloudflared tunnel --url http://localhost:5010
```

### 2. Получите URL туннеля
После запуска команды вы увидите что-то вроде:
```
2025-09-10T10:20:00Z INF | Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):
https://random-name-123.trycloudflare.com
```

### 3. Обновите webhook URL
Замените `random-name-123` на ваш URL:
- **Webhook URL**: `https://random-name-123.trycloudflare.com/webhook`
- **Base URL**: `https://random-name-123.trycloudflare.com`
- **Admin Panel**: `https://random-name-123.trycloudflare.com/admin`

### 4. Настройте в Express.ms
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Добавьте новое приложение:
   - **Название**: Flight Booking Bot
   - **Описание**: Бот для подачи заявок на командировочные рейсы
   - **URL приложения**: `https://random-name-123.trycloudflare.com`
   - **Webhook URL**: `https://random-name-123.trycloudflare.com/webhook`
   - **Иконка**: ✈️

### 5. Тестирование
1. Сохраните настройки в Express.ms
2. Проверьте статус бота (должен быть "онлайн")
3. Отправьте команду `/start` боту
4. Проверьте админ панель: `https://random-name-123.trycloudflare.com/admin`

## 🧪 Тестирование API:
```bash
# Health check
curl https://random-name-123.trycloudflare.com/health

# Manifest
curl https://random-name-123.trycloudflare.com/manifest

# Webhook test
curl -X POST https://random-name-123.trycloudflare.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

## 📊 Мониторинг:
- **Админ панель**: `https://random-name-123.trycloudflare.com/admin`
- **Статистика**: `https://random-name-123.trycloudflare.com/api/stats`
- **Логи**: `tail -f /root/test/express_bot/fixed_bot.log`

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

## 📞 Поддержка:
- Логи бота: `/root/test/express_bot/fixed_bot.log`
- Конфигурация: `/root/test/express_bot/config.json`
- Админ панель: `https://random-name-123.trycloudflare.com/admin`
