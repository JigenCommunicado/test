#!/bin/bash
echo "Устанавливаем зависимости для admin_server.py..."

# Активируем виртуальное окружение если оно есть
if [ -d "venv" ]; then
    echo "Активируем виртуальное окружение..."
    source venv/bin/activate
fi

# Устанавливаем зависимости
echo "Устанавливаем Flask и связанные пакеты..."
pip install flask==2.3.3
pip install flask-cors==4.0.0
pip install psutil
pip install openpyxl==3.1.2

# Проверяем установку
echo "Проверяем установку Flask..."
python3 -c "import flask; print('Flask версия:', flask.__version__)"

echo "Готово!"


