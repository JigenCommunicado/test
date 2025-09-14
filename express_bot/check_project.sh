#!/bin/bash
# Скрипт проверки состояния всего проекта

cd /root/test/express_bot

echo "🔍 Express SmartApp - Проверка проекта"
echo "====================================="
echo ""

# Проверка структуры
echo "📁 Структура проекта:"
echo "├── backend/ ($(find backend -name "*.py" | wc -l) Python файлов)"
echo "├── frontend/ ($(find frontend -name "*.html" | wc -l) HTML файлов)"
echo "├── scripts/ ($(find scripts -name "*.sh" | wc -l) скриптов)"
echo "├── telegram_components/ ($(find telegram_components -name "*.py" -o -name "*.html" | wc -l) файлов)"
echo "├── config/ ($(find config -name "*.py" -o -name "*.txt" -o -name "*.env" | wc -l) конфигов)"
echo "├── docs/ ($(find docs -name "*.md" | wc -l) документов)"
echo "└── static/ ($(find static -name "*.json" -o -name "*.js" | wc -l) статических файлов)"
echo ""

# Проверка основных файлов
echo "📋 Основные файлы:"
echo "├── manage_all.sh $(test -f manage_all.sh && echo "✅" || echo "❌")"
echo "├── README.md $(test -f README.md && echo "✅" || echo "❌")"
echo "├── QUICK_START.md $(test -f QUICK_START.md && echo "✅" || echo "❌")"
echo "└── CLEANUP_REPORT.md $(test -f CLEANUP_REPORT.md && echo "✅" || echo "❌")"
echo ""

# Проверка серверов
echo "🔧 Статус серверов:"
if pgrep -f "smartapp_flight_booking.py" > /dev/null; then
    echo "├── Flask API (порт 5002): ✅ Запущен"
else
    echo "├── Flask API (порт 5002): ❌ Остановлен"
fi

if pgrep -f "python3 -m http.server" > /dev/null; then
    echo "├── Static Server (порт 8080): ✅ Запущен"
else
    echo "├── Static Server (порт 8080): ❌ Остановлен"
fi

if pgrep -f "telegram_bot" > /dev/null; then
    echo "├── Telegram Bot: ✅ Запущен"
else
    echo "├── Telegram Bot: ❌ Остановлен"
fi

if curl -s "https://bp-primary-aluminum-start.trycloudflare.com/telegram_mini_app_adaptive.html" > /dev/null 2>&1; then
    echo "└── Mini App: ✅ Доступен"
else
    echo "└── Mini App: ❌ Недоступен"
fi
echo ""

# Проверка логов
echo "📋 Логи:"
if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
    echo "├── Основные логи: ✅ Есть ($(ls logs/*.log 2>/dev/null | wc -l) файлов)"
else
    echo "├── Основные логи: ❌ Пусто"
fi

if [ -d "telegram_components/logs" ] && [ "$(ls -A telegram_components/logs 2>/dev/null)" ]; then
    echo "└── Telegram логи: ✅ Есть ($(ls telegram_components/logs/*.log 2>/dev/null | wc -l) файлов)"
else
    echo "└── Telegram логи: ❌ Пусто"
fi
echo ""

# Рекомендации
echo "💡 Рекомендации:"
if ! pgrep -f "smartapp_flight_booking.py" > /dev/null; then
    echo "├── Запустите основную систему: ./manage_all.sh start"
fi
if ! pgrep -f "telegram_bot" > /dev/null; then
    echo "├── Запустите Telegram бота: ./telegram_components/manage_telegram.sh start"
fi
if [ ! -f "venv/bin/activate" ]; then
    echo "├── Создайте виртуальное окружение: python3 -m venv venv"
fi
echo "└── Проверьте документацию: cat README.md"
echo ""

echo "🎯 Проект готов к использованию!"
