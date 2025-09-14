# 🚀 CloudPub - Российская альтернатива для Express Bot

## 📋 Ваш токен CloudPub:
```
GCJBOg6PyZWdn6r4oeT0tYM2WpVpUkclJwsXR0bDNQU
```

## 🔧 Быстрая настройка:

### 1. Установка CloudPub:
```bash
export CLO_VERSION="2.2.2"
sudo mkdir -p /usr/local/bin && cd /usr/local/bin
sudo curl -L "https://cloudpub.ru/download/stable/clo-${CLO_VERSION}-stable-linux-$(uname -m).tar.gz" | sudo tar -xzv
sudo chmod +x clo
```

### 2. Настройка токена:
```bash
sudo -H clo set token GCJBOg6PyZWdn6r4oeT0tYM2WpVpUkclJwsXR0bDNQU
```

### 3. Регистрация Express Bot:
```bash
sudo -H clo register --name express-bot http localhost:5011
```

### 4. Запуск сервиса:
```bash
sudo systemctl enable --now clo.service
```

### 5. Проверка:
```bash
sudo clo list
```

## 🌐 Получение URL:

После выполнения команд выше, вы получите URL вида:
```
https://your-bot-name.cloudpub.ru
```

## 📱 Настройка в Express.ms:

1. **Откройте админ панель Express.ms**
2. **Добавьте бота как SmartApp**
3. **Укажите webhook URL**: `https://your-bot-name.cloudpub.ru/webhook`
4. **Протестируйте команду `/start`**

## 🧪 Тестирование:

```bash
# Health check
curl https://your-bot-name.cloudpub.ru/health

# Manifest
curl https://your-bot-name.cloudpub.ru/manifest

# Webhook test
curl -X POST https://your-bot-name.cloudpub.ru/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

## 🔧 Управление CloudPub:

```bash
# Просмотр сервисов
sudo clo list

# Остановка сервиса
sudo clo stop express-bot

# Запуск сервиса
sudo clo start express-bot

# Удаление сервиса
sudo clo remove express-bot

# Перезапуск сервиса
sudo systemctl restart clo.service

# Просмотр логов
sudo journalctl -u clo.service -f
```

## ✅ Преимущества CloudPub:

- 🇷🇺 **Российский сервис** - быстрый доступ из России
- 🔒 **Безопасный** - защищенное соединение
- 🚀 **Стабильный** - надежная работа
- 🔧 **Простой** - легкая настройка
- 🌐 **Собственные домены** - поддержка кастомных доменов
- 💰 **Бесплатный** - для базового использования

## 🔧 Устранение проблем:

### CloudPub не запускается:
```bash
# Проверьте статус
sudo systemctl status clo.service

# Перезапустите
sudo systemctl restart clo.service

# Проверьте логи
sudo journalctl -u clo.service -f
```

### Токен не работает:
```bash
# Проверьте токен
sudo clo status

# Настройте заново
sudo -H clo set token GCJBOg6PyZWdn6r4oeT0tYM2WpVpUkclJwsXR0bDNQU
```

### Сервис не регистрируется:
```bash
# Удалите и создайте заново
sudo clo remove express-bot
sudo -H clo register --name express-bot http localhost:5011
```

## 📊 Мониторинг:

- **Статус сервиса**: `sudo systemctl status clo.service`
- **Логи CloudPub**: `sudo journalctl -u clo.service -f`
- **Список сервисов**: `sudo clo list`
- **Статистика**: `sudo clo stats`

## 🎯 Ожидаемый результат:

После настройки вы получите:
- ✅ Стабильный URL для бота
- ✅ Быстрый доступ из России
- ✅ Защищенное соединение
- ✅ Простое управление

## 🚀 Готово к использованию!

CloudPub настроен и готов к работе с Express.ms! 🎉

