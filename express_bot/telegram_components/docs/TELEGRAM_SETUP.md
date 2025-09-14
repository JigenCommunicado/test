# 🤖 Настройка Telegram бота для системы подачи заявок

## 📋 Пошаговая инструкция

### 1. 🆕 Создание Telegram бота

1. **Найдите @BotFather в Telegram**
   - Откройте Telegram
   - Найдите пользователя `@BotFather`
   - Начните диалог

2. **Создайте нового бота**
   ```
   /start
   /newbot
   ```

3. **Настройте бота**
   - Введите название бота: `Flight Booking Bot`
   - Введите username бота: `your_flight_booking_bot` (должен заканчиваться на `bot`)
   - Получите токен бота (сохраните его!)

4. **Настройте описание и команды**
   ```
   /setdescription
   ```
   Описание:
   ```
   Бот для подачи заявок на корпоративные рейсы. Поддерживает веб-приложения для удобного заполнения форм.
   ```

   ```
   /setcommands
   ```
   Команды:
   ```
   start - Главное меню
   help - Справка по использованию
   status - Статус системы
   pc_version - ПК версия системы
   mobile_version - Мобильная версия
   admin - Панель администратора
   ```

### 2. 🔧 Настройка Mini App

1. **Настройте Mini App через @BotFather**
   ```
   /mybots
   [Выберите вашего бота]
   Bot Settings
   Menu Button
   Configure Menu Button
   ```

2. **Укажите URL Mini App**
   ```
   URL: http://localhost:8080/telegram_mini_app.html
   Text: ✈️ Подать заявку
   ```

### 3. 🚀 Запуск бота

1. **Установите зависимости**
   ```bash
   cd /root/test/express_bot
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Установите токен бота**
   ```bash
   export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
   ```
   
   Или создайте файл `.env`:
   ```bash
   echo "TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE" > .env
   ```

3. **Запустите бота**
   ```bash
   python3 telegram_bot.py
   ```

### 4. 📱 Настройка для продакшена

Для работы Mini App в продакшене нужен HTTPS. Варианты решения:

#### Вариант A: Ngrok (для тестирования)
```bash
# Установите ngrok
npm install -g ngrok

# Запустите туннель для статического сервера
ngrok http 8080

# Запустите туннель для API сервера  
ngrok http 5002
```

Обновите URL в коде:
- В `telegram_bot.py`: измените `mini_app_url`
- В `telegram_mini_app.html`: измените API URL

#### Вариант B: Cloudflare Tunnel
```bash
# Установите cloudflared
# Настройте туннель для вашего домена
cloudflared tunnel --url http://localhost:8080
```

#### Вариант C: VPS с доменом
- Разместите приложение на VPS
- Настройте домен с SSL сертификатом
- Обновите URL в настройках бота

### 5. 🧪 Тестирование

1. **Запустите все сервисы**
   ```bash
   # В первом терминале - Flask API
   cd /root/test/express_bot
   source venv/bin/activate
   python3 smartapp_flight_booking.py

   # Во втором терминале - Статический сервер
   cd /root/test/express_bot  
   python3 -m http.server 8080

   # В третьем терминале - Telegram бот
   cd /root/test/express_bot
   source venv/bin/activate
   export TELEGRAM_BOT_TOKEN="YOUR_TOKEN"
   python3 telegram_bot.py
   ```

2. **Протестируйте функции**
   - Найдите вашего бота в Telegram
   - Отправьте `/start`
   - Попробуйте команды: `/help`, `/status`
   - Нажмите "✈️ Подать заявку" для тестирования Mini App

### 6. 🎯 Основные возможности

**Команды бота:**
- `/start` - Главное меню с кнопками
- `/help` - Справка по использованию
- `/status` - Проверка работы API
- `/pc_version` - Ссылки на веб-версию
- `/mobile_version` - Открытие Mini App
- `/admin` - Ссылка на админ панель

**Mini App функции:**
- 📱 Адаптивный интерфейс для мобильных
- 🎨 Тема в стиле Telegram
- 📝 Пошаговое заполнение заявки
- ✅ Валидация данных
- 🔄 Автоматическое заполнение из профиля Telegram
- 📊 Предпросмотр данных перед отправкой

**Интеграции:**
- 🔗 Связь с основной системой через API
- 💾 Сохранение заявок в Excel
- 📈 Статистика и аналитика
- 🔔 Уведомления (при наличии Express интеграции)

### 7. 🛠️ Устранение неполадок

**Бот не отвечает:**
```bash
# Проверьте токен
echo $TELEGRAM_BOT_TOKEN

# Проверьте логи
python3 telegram_bot.py
```

**Mini App не загружается:**
- Убедитесь что статический сервер запущен на порту 8080
- Для продакшена нужен HTTPS
- Проверьте URL в настройках бота через @BotFather

**API ошибки:**
- Убедитесь что Flask сервер запущен на порту 5002
- Проверьте доступность через `curl http://localhost:5002/health`
- Для CORS ошибок - проверьте настройки в `smartapp_flight_booking.py`

**Проблемы с зависимостями:**
```bash
# Переустановите зависимости
pip install --upgrade -r requirements.txt

# Для проблем с aiohttp на старых системах
pip install aiohttp==3.8.6
```

### 8. 📊 Мониторинг

**Логи бота:**
```bash
# Запуск с детальными логами
python3 telegram_bot.py 2>&1 | tee telegram_bot.log
```

**Статистика использования:**
- Количество пользователей: проверьте в коде бота
- Заявки: через админ панель или API `/api/statistics`
- Ошибки: в логах Flask сервера

### 9. 🔒 Безопасность

**Рекомендации:**
- Не публикуйте токен бота в коде
- Используйте переменные окружения
- Для продакшена добавьте авторизацию
- Ограничьте доступ к админ функциям
- Настройте rate limiting для API

**Проверка токена:**
```bash
# Тест через API Telegram
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

## 🎉 Готово!

Теперь у вас есть полнофункциональный Telegram бот с Mini App для системы подачи заявок на корпоративные рейсы!

**Возможности:**
- ✅ Обычные команды бота
- ✅ Веб-приложение (Mini App) 
- ✅ Интеграция с основной системой
- ✅ Сохранение данных
- ✅ Мобильная оптимизация
