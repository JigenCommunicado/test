
# 🚀 Инструкции по настройке Express Bot в Express.ms

## 📋 Информация о боте:
- **Bot ID**: 00c46d64-1127-5a96-812d-3d8b27c58b99
- **Webhook URL**: https://comparing-doom-solving-royalty.trycloudflare.com:5010/webhook
- **Base URL**: https://comparing-doom-solving-royalty.trycloudflare.com:5010
- **Admin Panel**: https://comparing-doom-solving-royalty.trycloudflare.com:5010/admin

## 🔧 Шаги настройки в Express.ms:

### 1. Регистрация бота как SmartApp
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps" или "Приложения"
3. Нажмите "Добавить новое приложение"
4. Заполните поля:
   - **Название**: Flight Booking Bot
   - **Описание**: Бот для подачи заявок на командировочные рейсы
   - **URL приложения**: https://comparing-doom-solving-royalty.trycloudflare.com:5010
   - **Webhook URL**: https://comparing-doom-solving-royalty.trycloudflare.com:5010/webhook
   - **Иконка**: ✈️
   - **Цвет**: #0088cc

### 2. Настройка webhook
1. В настройках бота укажите:
   - **Webhook URL**: https://comparing-doom-solving-royalty.trycloudflare.com:5010/webhook
   - **События**: message, command, callback_query
   - **Метод**: POST
   - **Content-Type**: application/json

### 3. Настройка прав доступа
Убедитесь, что бот имеет права:
- ✅ Чтение сообщений
- ✅ Отправка сообщений
- ✅ Чтение информации о пользователях
- ✅ Доступ к файлам

### 4. Тестирование
1. Сохраните настройки
2. Проверьте статус бота (должен быть "онлайн")
3. Отправьте команду `/start` боту
4. Проверьте админ панель: https://comparing-doom-solving-royalty.trycloudflare.com:5010/admin

## 🧪 Тестирование через API:
```bash
# Health check
curl https://comparing-doom-solving-royalty.trycloudflare.com:5010/health

# Manifest
curl https://comparing-doom-solving-royalty.trycloudflare.com:5010/manifest

# Webhook test
curl -X POST https://comparing-doom-solving-royalty.trycloudflare.com:5010/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

## 📊 Мониторинг:
- **Админ панель**: https://comparing-doom-solving-royalty.trycloudflare.com:5010/admin
- **Логи**: tail -f /root/test/express_bot/fixed_bot.log
- **Статистика**: https://comparing-doom-solving-royalty.trycloudflare.com:5010/api/stats

## 🔧 Устранение проблем:
1. **Бот оффлайн**: Проверьте webhook URL и права доступа
2. **Ошибки webhook**: Проверьте логи бота
3. **Не отвечает**: Проверьте статус сервера

## 📞 Поддержка:
- Логи бота: /root/test/express_bot/fixed_bot.log
- Конфигурация: /root/test/express_bot/express_ms_config.json
- Админ панель: https://comparing-doom-solving-royalty.trycloudflare.com:5010/admin


