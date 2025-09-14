# 🤖 Telegram Components

Все компоненты, связанные с Telegram ботом и Mini App.

## 📁 Структура папок

```
telegram_components/
├── bots/                    # Telegram боты
│   ├── telegram_bot_test.py
│   └── telegram_bot_mini_app.py
├── mini_apps/              # Telegram Mini Apps
│   ├── telegram_mini_app_adaptive.html
│   └── telegram_mini_app_mobile_safe.html
├── scripts/                # Скрипты запуска/остановки
│   ├── start_telegram_bot.sh
│   ├── start_final_mini_app.sh
│   └── stop_*.sh
├── docs/                   # Документация
│   ├── TELEGRAM_SETUP.md
│   ├── TELEGRAM_TEST_GUIDE.md
│   └── MINI_APP_TEST_GUIDE.md
└── logs/                   # Логи
    └── telegram_bot_*.log
```

## 🚀 Быстрый запуск

### 1. Запуск бота:
```bash
cd /root/test/express_bot/telegram_components/scripts
./start_telegram_bot.sh
```

### 2. Запуск Mini App:
```bash
cd /root/test/express_bot/telegram_components/scripts
./start_final_mini_app.sh
```

## 🔧 Основные файлы

- **`bots/telegram_bot_test.py`** - Основной бот с полным функционалом
- **`mini_apps/telegram_mini_app_adaptive.html`** - Адаптивный Mini App
- **`scripts/start_final_mini_app.sh`** - Скрипт запуска с Cloudflare туннелем

## 📱 Mini App URL

```
https://bp-primary-aluminum-start.trycloudflare.com/telegram_mini_app_adaptive.html
```

## 🎯 Тестирование

1. Откройте `@ExpressSmartAppBot` в Telegram
2. Отправьте `/start`
3. Нажмите "🚀 Mini App"
4. Заполните и отправьте заявку

## 📋 Статус

- ✅ Бот работает
- ✅ Mini App доступен
- ✅ Cloudflare туннель активен
- ✅ API интеграция работает
