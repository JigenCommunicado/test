#!/usr/bin/env python3
"""
Тестирование Express Bot с LocalTunnel
"""

import requests
import json
import time
import sys

def test_endpoint(url, name, expected_status=200):
    """Тестирование endpoint"""
    try:
        print(f"🧪 Тестируем {name}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == expected_status:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

def test_webhook(url, name):
    """Тестирование webhook"""
    try:
        print(f"🧪 Тестируем {name}...")
        
        test_data = {
            "type": "message",
            "user_id": "test_user_123",
            "text": "/start",
            "timestamp": int(time.time())
        }
        
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование Express Bot с LocalTunnel")
    print("=" * 50)
    
    base_url = "https://express-bot-flight.loca.lt"
    local_url = "http://localhost:5011"
    
    tests = [
        # Локальные тесты
        (f"{local_url}/health", "Local Health Check"),
        (f"{local_url}/manifest", "Local Manifest"),
        (f"{local_url}/admin", "Local Admin Panel"),
        (f"{local_url}/api/stats", "Local API Stats"),
        
        # Туннель тесты
        (f"{base_url}/health", "Tunnel Health Check"),
        (f"{base_url}/manifest", "Tunnel Manifest"),
        (f"{base_url}/admin", "Tunnel Admin Panel"),
        (f"{base_url}/api/stats", "Tunnel API Stats"),
    ]
    
    webhook_tests = [
        (f"{local_url}/webhook", "Local Webhook"),
        (f"{base_url}/webhook", "Tunnel Webhook"),
    ]
    
    print("\n1️⃣ Тестируем локальные endpoints...")
    local_results = []
    for url, name in tests[:4]:
        result = test_endpoint(url, name)
        local_results.append(result)
    
    print("\n2️⃣ Тестируем туннель endpoints...")
    tunnel_results = []
    for url, name in tests[4:]:
        result = test_endpoint(url, name)
        tunnel_results.append(result)
    
    print("\n3️⃣ Тестируем webhooks...")
    webhook_results = []
    for url, name in webhook_tests:
        result = test_webhook(url, name)
        webhook_results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 50)
    
    local_passed = sum(local_results)
    local_total = len(local_results)
    print(f"🏠 Локальные endpoints: {local_passed}/{local_total}")
    
    tunnel_passed = sum(tunnel_results)
    tunnel_total = len(tunnel_results)
    print(f"🌐 Туннель endpoints: {tunnel_passed}/{tunnel_total}")
    
    webhook_passed = sum(webhook_results)
    webhook_total = len(webhook_results)
    print(f"🔗 Webhooks: {webhook_passed}/{webhook_total}")
    
    total_passed = local_passed + tunnel_passed + webhook_passed
    total_tests = local_total + tunnel_total + webhook_total
    
    print(f"\n🎯 Общий результат: {total_passed}/{total_tests}")
    
    if total_passed == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n📋 Следующие шаги:")
        print("1. Откройте админ панель Express.ms")
        print("2. Добавьте бота как SmartApp")
        print(f"3. Укажите webhook URL: {base_url}/webhook")
        print("4. Протестируйте команду /start")
        return True
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("\n🔧 Рекомендации:")
        print("1. Проверьте, что бот запущен: ps aux | grep express_bot_localtunnel")
        print("2. Проверьте, что туннель работает: ps aux | grep localtunnel")
        print("3. Проверьте логи бота: tail -f localtunnel_bot.log")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

