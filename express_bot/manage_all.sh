#!/bin/bash
# Главный скрипт управления всем проектом Express SmartApp

cd /root/test/express_bot

echo "🚀 Express SmartApp - Главное управление"
echo "======================================="
echo ""

case "$1" in
    "start")
        echo "🚀 Запуск всей системы..."
        echo ""
        echo "1️⃣ Запускаем основную систему..."
        ./scripts/manage.sh start
        echo ""
        echo "2️⃣ Запускаем Telegram компоненты..."
        ./telegram_components/manage_telegram.sh start
        echo ""
        echo "✅ Вся система запущена!"
        ;;
    "stop")
        echo "🛑 Остановка всей системы..."
        echo ""
        echo "1️⃣ Останавливаем Telegram компоненты..."
        ./telegram_components/manage_telegram.sh stop
        echo ""
        echo "2️⃣ Останавливаем основную систему..."
        ./scripts/manage.sh stop
        echo ""
        echo "✅ Вся система остановлена!"
        ;;
    "restart")
        echo "🔄 Перезапуск всей системы..."
        $0 stop
        sleep 3
        $0 start
        ;;
    "status")
        echo "📊 Статус всей системы..."
        echo ""
        echo "🔧 Основная система:"
        ./scripts/manage.sh status
        echo ""
        echo "🤖 Telegram компоненты:"
        ./telegram_components/manage_telegram.sh status
        ;;
    "logs")
        echo "📋 Логи системы..."
        echo ""
        echo "🔧 Основные логи:"
        tail -10 logs/*.log 2>/dev/null || echo "Логи не найдены"
        echo ""
        echo "🤖 Telegram логи:"
        tail -10 telegram_components/logs/*.log 2>/dev/null || echo "Логи не найдены"
        ;;
    "clean")
        echo "🧹 Очистка логов и временных файлов..."
        rm -f logs/*.log
        rm -f telegram_components/logs/*.log
        rm -f *.pid
        echo "✅ Очистка завершена!"
        ;;
    "help"|"")
        echo "📋 Доступные команды:"
        echo "  start    - Запустить всю систему"
        echo "  stop     - Остановить всю систему"
        echo "  restart  - Перезапустить всю систему"
        echo "  status   - Показать статус всех компонентов"
        echo "  logs     - Показать логи"
        echo "  clean    - Очистить логи и временные файлы"
        echo "  help     - Показать эту справку"
        echo ""
        echo "Примеры:"
        echo "  ./manage_all.sh start"
        echo "  ./manage_all.sh status"
        echo ""
        echo "📁 Структура проекта:"
        echo "  backend/          - Backend компоненты"
        echo "  frontend/         - Frontend компоненты"
        echo "  scripts/          - Скрипты управления"
        echo "  telegram_components/ - Telegram бот и Mini App"
        echo "  config/           - Конфигурация"
        echo "  docs/             - Документация"
        ;;
    *)
        echo "❌ Неизвестная команда: $1"
        echo "Используйте: ./manage_all.sh help"
        ;;
esac
