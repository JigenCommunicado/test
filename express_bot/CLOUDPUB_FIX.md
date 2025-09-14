# 🔧 Исправление CloudPub

## ❌ Проблема:
CloudPub не может подключиться к локальному боту (503 ошибка)

## ✅ Решение:

### 1. Проверьте статус CloudPub:
```bash
sudo clo ls
```

### 2. Удалите старый сервис:
```bash
sudo clo remove express-bot
```

### 3. Регистрируйте заново:
```bash
sudo -H clo register --name express-bot http localhost:5011
```

### 4. Проверьте результат:
```bash
sudo clo ls
```

### 5. Протестируйте:
```bash
curl https://loosely-welcoming-grackle.cloudpub.ru/health
```

## 🚀 Альтернативные решения:

### LocalTunnel (рекомендуется):
```bash
# Остановите CloudPub
sudo clo remove express-bot

# Запустите LocalTunnel
npx localtunnel --port 5011

# Получите новый URL
```

### Cloudflare Tunnel:
```bash
# Остановите CloudPub
sudo clo remove express-bot

# Запустите Cloudflare
cloudflared tunnel --url http://localhost:5011

# Получите новый URL
```

## 📱 Настройка в Express.ms:

1. Получите рабочий URL туннеля
2. Обновите конфигурацию:
   ```json
   {
     "bot_settings": {
       "webhook_url": "https://YOUR_TUNNEL_URL/webhook",
       "api_base_url": "https://YOUR_TUNNEL_URL"
     }
   }
   ```
3. Настройте webhook в Express.ms
4. Протестируйте команду `/start`

## ✅ Готово!

Ваш бот работает локально и готов к интеграции! 🚀

