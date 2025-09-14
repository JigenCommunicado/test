#!/bin/bash

# Скрипт запуска Final Express Bot
echo "🚀 Запуск Express Flight Booking Bot..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем конфигурацию
echo "🔧 Проверка конфигурации..."
python3 express_bot_config.py

if [ $? -ne 0 ]; then
    echo "❌ Ошибка в конфигурации. Проверьте настройки."
    exit 1
fi

# Останавливаем предыдущие процессы
echo "🛑 Остановка предыдущих процессов..."
pkill -f express_bot.py 2>/dev/null
pkill -f express_bot_webhook_server.py 2>/dev/null
pkill -f express_bot_enhanced.py 2>/dev/null
pkill -f express_bot_final.py 2>/dev/null

# Ждем завершения процессов
sleep 2

# Запускаем Express Bot Webhook Server
echo "🤖 Запуск Express Bot Webhook Server..."
nohup python3 express_bot_webhook.py > bot.log 2>&1 &
BOT_PID=$!

# Ждем запуска
sleep 3

# Проверяем статус
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Express Bot запущен успешно (PID: $BOT_PID)"
    echo "📋 Логи: tail -f bot.log"
    echo "🔗 Webhook URL: https://comparing-doom-solving-royalty.trycloudflare.com/webhook"
    echo ""
    echo "🎯 Финальные возможности (на основе кода из скриншотов):"
    echo "• ✨ Полная поддержка инлайн кнопок"
    echo "• 📅 Интерактивный календарь с навигацией"
    echo "• 🏢 Выбор ОКЭ по локациям"
    echo "• 🌍 Направления по локациям"
    echo "• 🔄 Полная навигация с кнопками 'Назад'"
    echo "• ✅ Подтверждение данных перед отправкой"
    echo "• 📝 Поддержка ручного ввода направления"
    echo "• 💾 Сохранение последних данных пользователя"
    echo "• 🎨 Интерфейс как в оригинальных скриншотах"
    echo ""
    echo "📱 Команды бота:"
    echo "• /start - Начать работу с полным интерфейсом"
    echo ""
    echo "🎮 Полный процесс подачи заявки:"
    echo "1. Выбор локации (Москва, СПб, Красноярск, Сочи)"
    echo "2. Выбор ОКЭ (зависит от локации)"
    echo "3. Выбор даты через календарь"
    echo "4. Выбор должности (БП, БП BS, СБЭ, ИПБ)"
    echo "5. Ввод ФИО и табельного номера"
    echo "6. Выбор направления (из списка или ручной ввод)"
    echo "7. Ввод пожеланий"
    echo "8. Подтверждение заявки"
else
    echo "❌ Ошибка запуска Express Bot"
    echo "📋 Проверьте логи: cat bot.log"
    exit 1
fi

echo ""
echo "🎯 Express Bot готов к работе!"
echo "💡 Для остановки: pkill -f express_bot_webhook.py"
