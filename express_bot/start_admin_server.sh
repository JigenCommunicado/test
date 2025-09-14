#!/bin/bash
echo "🚀 Запуск Admin Panel Server..."

# Переходим в директорию проекта
cd /root/test/express_bot

# Проверяем существование виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "   Создайте его командой: python3 -m venv venv"
    echo "   Затем установите зависимости: source venv/bin/activate && pip install flask flask-cors psutil openpyxl"
    exit 1
fi

# Активируем виртуальное окружение
echo "📦 Активация виртуального окружения..."
source venv/bin/activate

# Проверяем установку Flask
echo "🔍 Проверка зависимостей..."
python3 -c "import flask, flask_cors, psutil, openpyxl; print('✅ Все зависимости установлены')" || {
    echo "❌ Не все зависимости установлены!"
    echo "   Установите их командой: pip install flask flask-cors psutil openpyxl"
    exit 1
}

# Запускаем admin server
echo "🌐 Запуск сервера..."
python3 admin_server.py
