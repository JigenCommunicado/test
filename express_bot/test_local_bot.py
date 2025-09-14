#!/usr/bin/env python3
"""
Тестирование локального Express Bot
"""

import requests
import json
import time

def test_endpoint(url, name, expected_status=200):
    """Тестирование endpoint"""
    try:
        print(f"🧪 Тестируем {name}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == expected_status:
            print(f"✅ {name}: OK ({response.status_code})")
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                if 'status' in data:
                    print(f"   📊 Статус: {data['status']}")
                if 'bot_id' in data:
                    print(f"   🤖 Bot ID: {data['bot_id']}")
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
        
        response = requests.post(url, json=test_data, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ {name}: OK ({response.status_code})")
            data = response.json()
            if 'status' in data:
                print(f"   📊 Ответ: {data['status']}")
            return True
        else:
            print(f"❌ {name}: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование локального Express Bot")
    print("=" * 50)
    
    base_url = "http://localhost:5011"
    
    tests = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/manifest", "Manifest"),
        (f"{base_url}/admin", "Admin Panel"),
        (f"{base_url}/api/stats", "API Stats"),
    ]
    
    webhook_tests = [
        (f"{base_url}/webhook", "Webhook"),
    ]
    
    print("\n1️⃣ Тестируем endpoints...")
    endpoint_results = []
    for url, name in tests:
        result = test_endpoint(url, name)
        endpoint_results.append(result)
    
    print("\n2️⃣ Тестируем webhook...")
    webhook_results = []
    for url, name in webhook_tests:
        result = test_webhook(url, name)
        webhook_results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 50)
    
    endpoint_passed = sum(endpoint_results)
    endpoint_total = len(endpoint_results)
    print(f"🔗 Endpoints: {endpoint_passed}/{endpoint_total}")
    
    webhook_passed = sum(webhook_results)
    webhook_total = len(webhook_results)
    print(f"🔗 Webhooks: {webhook_passed}/{webhook_total}")
    
    total_passed = endpoint_passed + webhook_passed
    total_tests = endpoint_total + webhook_total
    
    print(f"\n🎯 Общий результат: {total_passed}/{total_tests}")
    
    if total_passed == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n📋 Локальный бот работает корректно!")
        print(f"🌐 Локальный URL: {base_url}")
        print(f"👨‍💼 Админ панель: {base_url}/admin")
        print(f"🔗 Webhook: {base_url}/webhook")
        return True
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("\n🔧 Рекомендации:")
        print("1. Проверьте, что бот запущен: ps aux | grep express_bot_localtunnel")
        print("2. Проверьте порт 5011: netstat -tlnp | grep 5011")
        print("3. Проверьте логи бота: tail -f localtunnel_bot.log")
        return False

if __name__ == "__main__":
    main()

