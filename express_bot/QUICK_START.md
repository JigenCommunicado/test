# 🚀 Express SmartApp - Быстрый старт

## 📁 Проект полностью структурирован!

### 🎯 Главное управление:
```bash
cd /root/test/express_bot
./manage_all.sh start    # Запустить всё
./manage_all.sh status   # Проверить статус
./manage_all.sh stop     # Остановить всё
```

### 📂 Структура папок:

```
express_bot/
├── backend/              # Python backend файлы
├── frontend/             # HTML интерфейсы
├── scripts/              # Скрипты управления
├── telegram_components/  # Telegram бот и Mini App
├── config/               # Конфигурация
├── docs/                 # Документация
├── logs/                 # Логи
├── static/               # Статические файлы
└── data/                 # Данные (Excel)
```

### 🔧 Управление компонентами:

#### Основная система:
```bash
./scripts/manage.sh start|stop|restart|status
```

#### Telegram компоненты:
```bash
./telegram_components/manage_telegram.sh start|stop|status
```

### 🌐 Доступ к системе:

- **Веб-интерфейс:** http://localhost:8080/index.html
- **Telegram бот:** @ExpressSmartAppBot
- **Mini App:** https://bp-primary-aluminum-start.trycloudflare.com/telegram_mini_app_adaptive.html

### ✅ Готово к использованию!

Все компоненты организованы и готовы к работе.
