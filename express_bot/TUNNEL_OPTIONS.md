# 🌐 Варианты туннелей для Express Bot

## ✅ Работающие туннели:

### 1. **LocalTunnel** (Текущий)
```bash
npx localtunnel --port 5011
# URL: https://five-flies-read.loca.lt
```
**Плюсы**: Бесплатный, простой, не требует регистрации
**Минусы**: Может быть нестабильным, URL меняется

### 2. **Cloudflare Tunnel**
```bash
cloudflared tunnel --url http://localhost:5011
# URL: https://pilot-ana-wu-gui.trycloudflare.com
```
**Плюсы**: Стабильный, быстрый, от Cloudflare
**Минусы**: URL меняется при перезапуске

## 🔧 Альтернативные туннели:

### 3. **Serveo** (SSH-based)
```bash
ssh -R 80:localhost:5011 serveo.net
# URL: https://[random-name].serveo.net
```
**Плюсы**: SSH-based, стабильный
**Минусы**: Требует SSH, может блокироваться

### 4. **ngrok** (Профессиональный)
```bash
# Установка
wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
unzip /tmp/ngrok.zip -d /usr/local/bin/
chmod +x /usr/local/bin/ngrok

# Настройка (требует токен)
ngrok config add-authtoken YOUR_TOKEN
ngrok http 5011
# URL: https://[random-name].ngrok.io
```
**Плюсы**: Очень стабильный, много функций
**Минусы**: Требует регистрации, лимиты на бесплатном плане

### 5. **Bore** (Rust-based)
```bash
# Установка
wget https://github.com/ekzhang/bore/releases/latest/download/bore-v0.5.0-x86_64-unknown-linux-musl.tar.gz
tar -xzf bore-v0.5.0-x86_64-unknown-linux-musl.tar.gz
chmod +x bore

# Запуск
./bore local 5011 --to bore.pub
# URL: https://bore.pub/[random-port]
```
**Плюсы**: Быстрый, легкий
**Минусы**: Менее популярный

### 6. **PageKite** (Python-based)
```bash
# Установка
pip install pagekite
# Запуск
python -m pagekite.py 5011 yourname.pagekite.me
# URL: https://yourname.pagekite.me
```
**Плюсы**: Python-based, настраиваемый
**Минусы**: Требует настройки

### 7. **SSH Port Forwarding** (С VPS)
```bash
ssh -R 80:localhost:5011 user@your-vps.com
# URL: http://your-vps.com
```
**Плюсы**: Полный контроль, стабильный
**Минусы**: Требует VPS

## 🎯 Рекомендации по использованию:

### Для разработки:
1. **LocalTunnel** - простой и быстрый
2. **Cloudflare Tunnel** - стабильный

### Для тестирования:
1. **ngrok** - профессиональный
2. **Serveo** - SSH-based

### Для продакшена:
1. **Собственный VPS** - полный контроль
2. **ngrok** - с платным планом
3. **Cloudflare Tunnel** - с аккаунтом

## 🧪 Текущая настройка:

**Активный туннель**: LocalTunnel
**URL**: `https://five-flies-read.loca.lt`
**Webhook**: `https://five-flies-read.loca.lt/webhook`
**Admin Panel**: `https://five-flies-read.loca.lt/admin`

## 🔄 Переключение туннелей:

### На LocalTunnel:
```bash
pkill -f cloudflared
npx localtunnel --port 5011
```

### На Cloudflare:
```bash
pkill -f localtunnel
cloudflared tunnel --url http://localhost:5011
```

### На ngrok:
```bash
pkill -f localtunnel
pkill -f cloudflared
ngrok http 5011
```

## 📱 Настройка в Express.ms:

1. Откройте админ панель Express.ms
2. Добавьте бота как SmartApp
3. Укажите webhook URL: `https://five-flies-read.loca.lt/webhook`
4. Протестируйте команду `/start`

## 🔧 Устранение проблем:

### Туннель не работает:
```bash
# Остановите все туннели
pkill -f localtunnel
pkill -f cloudflared
pkill -f ngrok

# Попробуйте другой туннель
npx localtunnel --port 5011
```

### URL изменился:
1. Обновите конфигурацию в `config.json`
2. Обновите webhook URL в Express.ms
3. Перезапустите бота

## ✅ Готово к использованию!

Ваш бот настроен и готов к работе с Express.ms! 🚀

