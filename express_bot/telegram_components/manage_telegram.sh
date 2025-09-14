#!/bin/bash
# Главный скрипт управления Telegram компонентами

cd /root/test/express_bot/telegram_components

echo "🤖 Управление Telegram компонентами"
echo "=================================="
echo ""

case "$1" in
    "start")
        echo "🚀 Запуск Telegram бота и Mini App..."
        ./scripts/start_final_mini_app.sh
        ;;
    "stop")
        echo "🛑 Остановка всех Telegram компонентов..."
        ./scripts/stop_final_mini_app.sh
        ;;
    "bot")
        echo "🤖 Запуск только бота..."
        ./scripts/start_telegram_bot.sh
        ;;
    "status")
        echo "📊 Статус Telegram компонентов..."
        echo ""
        echo "🤖 Бот:"
        ps aux | grep telegram_bot | grep -v grep || echo "❌ Не запущен"
        echo ""
        echo "🌐 Mini App:"
        if curl -s "https://bp-primary-aluminum-start.trycloudflare.com/telegram_mini_app_adaptive.html" > /dev/null 2>&1; then
            echo "✅ Доступен"
        else
            echo "❌ Недоступен"
        fi
        echo ""
        echo "📱 URL: https://bp-primary-aluminum-start.trycloudflare.com/telegram_mini_app_adaptive.html"
        ;;
    "logs")
        echo "📋 Логи Telegram бота:"
        tail -20 logs/telegram_bot_*.log 2>/dev/null || echo "Логи не найдены"
        ;;
    "help"|"")
        echo "📋 Доступные команды:"
        echo "  start  - Запустить бота и Mini App"
        echo "  stop   - Остановить все компоненты"
        echo "  bot    - Запустить только бота"
        echo "  status - Показать статус"
        echo "  logs   - Показать логи"
        echo "  help   - Показать эту справку"
        echo ""
        echo "Примеры:"
        echo "  ./manage_telegram.sh start"
        echo "  ./manage_telegram.sh status"
        ;;
    *)
        echo "❌ Неизвестная команда: $1"
        echo "Используйте: ./manage_telegram.sh help"
        ;;
esac
