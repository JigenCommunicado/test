#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации IDE
"""

import sys
import os

def check_python_path():
    print("🐍 Python путь:", sys.executable)
    print("📁 Рабочая директория:", os.getcwd())
    print("🔍 Python path:")
    for i, path in enumerate(sys.path):
        print(f"  {i+1}. {path}")

def check_imports():
    print("\n📦 Проверка импортов:")
    
    try:
        import flask
        print(f"  ✅ Flask: {flask.__file__}")
    except ImportError as e:
        print(f"  ❌ Flask: {e}")
    
    try:
        import flask_cors
        print(f"  ✅ Flask-CORS: {flask_cors.__file__}")
    except ImportError as e:
        print(f"  ❌ Flask-CORS: {e}")
    
    try:
        import psutil
        print(f"  ✅ psutil: {psutil.__file__}")
    except ImportError as e:
        print(f"  ❌ psutil: {e}")
    
    try:
        import openpyxl
        print(f"  ✅ openpyxl: {openpyxl.__file__}")
    except ImportError as e:
        print(f"  ❌ openpyxl: {e}")
    
    try:
        import excel_integration
        print(f"  ✅ excel_integration: {excel_integration.__file__}")
    except ImportError as e:
        print(f"  ❌ excel_integration: {e}")

def main():
    print("🔍 Проверка конфигурации IDE для Express Bot")
    print("=" * 50)
    
    check_python_path()
    check_imports()
    
    print("\n" + "=" * 50)
    print("✅ Проверка завершена!")

if __name__ == "__main__":
    main()


