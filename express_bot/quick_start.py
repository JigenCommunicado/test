#!/usr/bin/env python3
"""
Быстрый запуск исправленного Express бота
"""

import subprocess
import time
import os
import sys

def run_command(cmd):
    """Выполнение команды"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Команда: {cmd}")
        print(f"Код выхода: {result.returncode}")
        if result.stdout:
            print(f"Вывод: {result.stdout}")
        if result.stderr:
            print(f"Ошибки: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка выполнения команды: {e}")
        return False

def main():
    print("🚀 Быстрый запуск Express Bot...")
    
    # Переходим в директорию проекта
    os.chdir('/root/test/express_bot')
    
    # Останавливаем старые процессы
    print("\n🛑 Останавливаем старые процессы...")
    run_command("pkill -f 'express_bot' || true")
    run_command("pkill -f 'python3.*express' || true")
    time.sleep(2)
    
    # Проверяем порты
    print("\n🔍 Проверяем порты...")
    run_command("lsof -Pi :5007 -sTCP:LISTEN || echo 'Порт 5007 свободен'")
    
    # Запускаем исправленный бот
    print("\n🤖 Запускаем исправленный бот...")
    success = run_command("nohup python3 express_bot_fixed.py > fixed_bot.log 2>&1 &")
    
    if success:
        print("✅ Бот запущен в фоне")
        time.sleep(3)
        
        # Проверяем статус
        print("\n📊 Проверяем статус...")
        run_command("ps aux | grep express_bot_fixed | grep -v grep")
        
        # Тестируем health check
        print("\n🧪 Тестируем health check...")
        run_command("curl -s http://localhost:5007/health || echo 'Health check не прошел'")
        
        print("\n📝 Логи:")
        run_command("tail -5 fixed_bot.log")
        
        print("\n🎉 Готово!")
        print("📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99")
        print("🌐 Webhook URL: https://comparing-doom-solving-royalty.trycloudflare.com/webhook")
        print("🔗 Health Check: http://localhost:5007/health")
        print("📋 Manifest: http://localhost:5007/manifest")
        print("\n📝 Для просмотра логов: tail -f fixed_bot.log")
        
    else:
        print("❌ Ошибка запуска бота")
        print("📝 Проверьте логи: cat fixed_bot.log")

if __name__ == "__main__":
    main()


