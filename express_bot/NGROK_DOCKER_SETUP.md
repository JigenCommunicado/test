# 🐳 Express Bot с ngrok в Docker - Полная настройка

## 📋 Что было создано:

### 1. Docker Compose конфигурация
- `docker-compose.ngrok.yml` - основная конфигурация с ngrok
- `Dockerfile.ngrok` - Dockerfile с поддержкой ngrok
- `ngrok.yml` - конфигурация ngrok

### 2. Скрипты запуска
- `setup_ngrok_docker.py` - полный скрипт настройки
- `start_ngrok_docker.sh` - быстрый скрипт запуска
- `run_ngrok.sh` - простой скрипт запуска

### 3. Конфигурационные файлы
- `ngrok.yml` - конфигурация ngrok туннеля
- `.env` - переменные окружения (создается автоматически)

## 🚀 Быстрый запуск:

### Вариант 1: Простой запуск
```bash
cd /root/test/express_bot
chmod +x run_ngrok.sh
./run_ngrok.sh
```

### Вариант 2: Полная настройка
```bash
cd /root/test/express_bot
python3 setup_ngrok_docker.py
```

### Вариант 3: Ручной запуск
```bash
cd /root/test/express_bot
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

## 🐳 Docker сервисы:

1. **express-bot** - основной бот (порт 8000)
2. **ngrok** - туннель (веб-интерфейс: http://localhost:4040)
3. **postgres** - база данных (порт 5432)
4. **redis** - кэш (порт 6379)

## 🌐 Веб-интерфейсы:

- **ngrok веб-интерфейс**: http://localhost:4040
- **Bot health check**: http://localhost:8000/health
- **Bot stats**: http://localhost:8000/stats
- **Bot manifest**: http://localhost:8000/manifest

## 📊 Получение ngrok URL:

После запуска получите URL туннеля:
```bash
curl http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('tunnels'):
    print('Webhook URL:', data['tunnels'][0]['public_url'] + '/webhook')
"
```

## 🔧 Управление сервисами:

### Просмотр логов:
```bash
# Все сервисы
docker-compose -f docker-compose.ngrok.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.ngrok.yml logs -f express-bot
docker-compose -f docker-compose.ngrok.yml logs -f ngrok
```

### Остановка:
```bash
docker-compose -f docker-compose.ngrok.yml down
```

### Перезапуск:
```bash
docker-compose -f docker-compose.ngrok.yml restart express-bot
```

## 🔧 Настройка в Express.ms:

1. Откройте админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Добавьте новое приложение:
   - **Название**: Express Bot Docker
   - **URL приложения**: `{ngrok_url}`
   - **Webhook URL**: `{ngrok_url}/webhook`
   - **Описание**: Бот для Express.ms в Docker

## 🧪 Тестирование:

### Health check:
```bash
curl http://localhost:8000/health
```

### Webhook test:
```bash
curl -X POST {ngrok_url}/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

## 🔧 Устранение проблем:

1. **Сервисы не запускаются**: Проверьте логи `docker-compose logs`
2. **ngrok не работает**: Проверьте `docker-compose logs ngrok`
3. **База данных недоступна**: Проверьте `docker-compose logs postgres`
4. **Порты заняты**: Остановите другие сервисы на портах 8000, 4040, 5432, 6379

## 📞 Поддержка:

- Логи: `docker-compose -f docker-compose.ngrok.yml logs`
- Конфигурация: `docker-compose.ngrok.yml`
- ngrok веб-интерфейс: http://localhost:4040
- Переменные окружения: `.env`

## 🎯 Ожидаемый результат:

После настройки у вас будет:
- ✅ Работающий Express Bot в Docker
- ✅ Стабильный ngrok туннель
- ✅ Веб-интерфейс для мониторинга
- ✅ Готовый webhook URL для Express.ms
- ✅ Изолированная среда разработки

## 📝 Дополнительные файлы:

- `DOCKER_NGROK_SETUP_GUIDE.md` - подробная инструкция
- `setup_ngrok_docker.py` - полный скрипт настройки
- `start_ngrok_docker.sh` - быстрый запуск
- `run_ngrok.sh` - простой запуск
