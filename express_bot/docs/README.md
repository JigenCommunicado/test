# 🚀 Express SmartApp - Система подачи заявок на корпоративные рейсы

Современное веб-приложение для подачи заявок на корпоративные рейсы с админ панелью, системой уведомлений и управлением периодами.

## 🚀 ЗАПУСК СЕРВЕРА

### Быстрый запуск (рекомендуется)
```bash
cd /root/test/express_bot
./manage.sh
```

### Ручной запуск
```bash
# 1. Перейти в директорию проекта
cd /root/test/express_bot

# 2. Активировать виртуальное окружение
source venv/bin/activate

# 3. Запустить Flask API сервер (порт 5002)
python3 smartapp_flight_booking.py

# 4. В новом терминале запустить статический сервер (порт 8080)
python3 -m http.server 8080
```

### Управление серверами
```bash
# Запуск всех серверов
./start_servers.sh

# Остановка всех серверов
./stop_servers.sh

# Перезапуск всех серверов
./restart_servers.sh

# Проверка статуса
./status_servers.sh
```

## 📱 Доступные ссылки

### Основные страницы
- **Главная навигация**: http://localhost:8080/index.html
- **Форма заявки (ПК)**: http://localhost:8080/flight_booking_ui.html
- **Форма заявки (мобильная)**: http://localhost:8080/mobile_booking_ui.html
- **Админ панель**: http://localhost:8080/admin_panel.html

### Дополнительные функции
- **Управление периодами**: http://localhost:8080/application_periods.html
- **Поиск заявок**: http://localhost:8080/search_interface.html
- **Уведомления**: http://localhost:8080/notifications.html

### API Endpoints
- **Health Check**: http://localhost:5002/health
- **Статистика**: http://localhost:5002/api/statistics
- **Создание заявки**: http://localhost:5002/api/application

## 🎯 Основные функции

### ✨ Подача заявок
- Пошаговая форма с анимациями
- Адаптивный дизайн для мобильных устройств
- Валидация данных
- Автоматическое сохранение в Excel

### 🗓️ Управление периодами
- Создание периодов подачи заявок
- Настройка дат начала и окончания
- Статусы периодов (активен/неактивен)

### 🔔 Система уведомлений
- Push уведомления
- Расписание уведомлений
- Уведомления о периодах заявок

### 👥 Управление пользователями
- Роли и права доступа
- Аутентификация
- Сессии пользователей

### 📊 Аналитика
- Статистика заявок
- Отчеты по ОКЭ
- Экспорт данных

## 🛠️ Технические требования

### Системные требования
- Python 3.8+
- Linux/Windows/macOS
- 512MB RAM
- 100MB свободного места

### Зависимости
- Flask
- Flask-CORS
- openpyxl
- pandas

## 📁 Структура проекта

```
express_bot/
├── smartapp_flight_booking.py    # Основной Flask сервер
├── test_smartapp.py              # Тестовый SmartApp
├── excel_integration.py          # Работа с Excel
├── user_management.py            # Управление пользователями
├── notification_system.py        # Система уведомлений
├── *.html                        # HTML страницы
├── manage.sh                     # Главный скрипт управления
├── start_servers.sh              # Запуск серверов
├── stop_servers.sh               # Остановка серверов
├── restart_servers.sh            # Перезапуск серверов
├── status_servers.sh             # Проверка статуса
└── data/                         # Данные приложения
    └── все_заявки.xlsx           # Excel файл с заявками
```

## 🔧 Устранение неполадок

### Сервер не запускается
```bash
# Проверьте логи
tail -f smartapp.log

# Проверьте порты
lsof -i :5002
lsof -i :8080
```

### Порт занят
```bash
# Найдите процесс
lsof -i :5002

# Убейте процесс
kill -9 <PID>
```

### Ошибки зависимостей
```bash
# Переустановите зависимости
pip install -r requirements.txt
```

## 📝 Логи

- **Flask сервер**: `smartapp.log`
- **Статический сервер**: `static.log`

## 🎉 Готово!

Теперь вы можете легко управлять всеми серверами Express SmartApp одной командой!

Для получения дополнительной информации о батниках см. [BATCH_SCRIPTS.md](BATCH_SCRIPTS.md)