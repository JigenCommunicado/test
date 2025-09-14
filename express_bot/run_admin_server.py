#!/usr/bin/env python3
"""
Launcher для admin_server.py с автоматической активацией виртуального окружения
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Определяем пути
    script_dir = Path(__file__).parent.absolute()
    venv_python = script_dir / "venv" / "bin" / "python3"
    admin_server = script_dir / "admin_server.py"
    
    # Проверяем существование виртуального окружения
    if not venv_python.exists():
        print("❌ Виртуальное окружение не найдено!")
        print(f"   Ожидаемый путь: {venv_python}")
        print("   Создайте виртуальное окружение командой: python3 -m venv venv")
        sys.exit(1)
    
    # Проверяем существование admin_server.py
    if not admin_server.exists():
        print("❌ admin_server.py не найден!")
        print(f"   Ожидаемый путь: {admin_server}")
        sys.exit(1)
    
    print("🚀 Запуск Admin Panel Server с виртуальным окружением...")
    print(f"📁 Рабочая директория: {script_dir}")
    print(f"🐍 Python: {venv_python}")
    
    # Запускаем admin_server.py через виртуальное окружение
    try:
        subprocess.run([str(venv_python), str(admin_server)], cwd=str(script_dir))
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


