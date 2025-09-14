#!/usr/bin/env python3
"""
Финальное тестирование Express Bot с CloudPub
"""

import requests
import json
import time

def test_endpoint(url, name, expected_status=200):
    """Тестирование endpoint"""
    try:
        print(f"🧪 Тестируем {name}...")
        response = requests.get(url, timeout=10)
        
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
        
        response = requests.post(url, json=test_data, timeout=10)
        
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
    print("🚀 Финальное тестирование Express Bot с CloudPub")
    print("=" * 60)
    
    cloudpub_url = "https://loosely-welcoming-grackle.cloudpub.ru"
    local_url = "http://localhost:5011"
    
    print(f"🌐 CloudPub URL: {cloudpub_url}")
    print(f"🏠 Local URL: {local_url}")
    print()
    
    tests = [
        # Локальные тесты
        (f"{local_url}/health", "Local Health Check"),
        (f"{local_url}/manifest", "Local Manifest"),
        (f"{local_url}/admin", "Local Admin Panel"),
        (f"{local_url}/api/stats", "Local API Stats"),
        
        # CloudPub тесты
        (f"{cloudpub_url}/health", "CloudPub Health Check"),
        (f"{cloudpub_url}/manifest", "CloudPub Manifest"),
        (f"{cloudpub_url}/admin", "CloudPub Admin Panel"),
        (f"{cloudpub_url}/api/stats", "CloudPub API Stats"),
    ]
    
    webhook_tests = [
        (f"{local_url}/webhook", "Local Webhook"),
        (f"{cloudpub_url}/webhook", "CloudPub Webhook"),
    ]
    
    print("1️⃣ Тестируем локальные endpoints...")
    local_results = []
    for url, name in tests[:4]:
        result = test_endpoint(url, name)
        local_results.append(result)
    
    print("\n2️⃣ Тестируем CloudPub endpoints...")
    cloudpub_results = []
    for url, name in tests[4:]:
        result = test_endpoint(url, name)
        cloudpub_results.append(result)
    
    print("\n3️⃣ Тестируем webhooks...")
    webhook_results = []
    for url, name in webhook_tests:
        result = test_webhook(url, name)
        webhook_results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    local_passed = sum(local_results)
    local_total = len(local_results)
    print(f"🏠 Локальные endpoints: {local_passed}/{local_total}")
    
    cloudpub_passed = sum(cloudpub_results)
    cloudpub_total = len(cloudpub_results)
    print(f"🌐 CloudPub endpoints: {cloudpub_passed}/{cloudpub_total}")
    
    webhook_passed = sum(webhook_results)
    webhook_total = len(webhook_results)
    print(f"🔗 Webhooks: {webhook_passed}/{webhook_total}")
    
    total_passed = local_passed + cloudpub_passed + webhook_passed
    total_tests = local_total + cloudpub_total + webhook_total
    
    print(f"\n🎯 Общий результат: {total_passed}/{total_tests}")
    
    if total_passed == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n📋 Настройка в Express.ms:")
        print(f"1. Откройте админ панель Express.ms")
        print(f"2. Добавьте бота как SmartApp")
        print(f"3. Укажите webhook URL: {cloudpub_url}/webhook")
        print(f"4. Протестируйте команду /start")
        print(f"\n🌐 Ваши URL:")
        print(f"   Bot URL: {cloudpub_url}")
        print(f"   Webhook: {cloudpub_url}/webhook")
        print(f"   Admin: {cloudpub_url}/admin")
        return True
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("\n🔧 Рекомендации:")
        print("1. Проверьте, что бот запущен: ps aux | grep express_bot_localtunnel")
        print("2. Проверьте CloudPub: sudo clo ls")
        print("3. Проверьте порт 5011: netstat -tlnp | grep 5011")
        return False

if __name__ == "__main__":
    main()

