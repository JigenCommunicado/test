#!/usr/bin/env python3
"""
Тест всех компонентов Express Bot
"""

import asyncio
import aiohttp
import json
import time

async def test_all_components():
    """Тестирование всех компонентов бота"""
    print("🧪 Тестируем все компоненты Express Bot...")
    
    base_url = "https://comparing-doom-solving-royalty.trycloudflare.com:5010"
    
    async with aiohttp.ClientSession() as session:
        # 1. Health Check
        print("\n1️⃣ Тестируем Health Check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health Check OK: {data['status']}")
                    print(f"   Bot ID: {data['bot_id']}")
                    print(f"   Service: {data['service']}")
                else:
                    print(f"❌ Health Check Failed: {response.status}")
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
        
        # 2. Manifest
        print("\n2️⃣ Тестируем Manifest...")
        try:
            async with session.get(f"{base_url}/manifest") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Manifest OK: {data['name']} v{data['version']}")
                    print(f"   Commands: {len(data['commands'])}")
                else:
                    print(f"❌ Manifest Failed: {response.status}")
        except Exception as e:
            print(f"❌ Manifest Error: {e}")
        
        # 3. Admin Panel
        print("\n3️⃣ Тестируем Admin Panel...")
        try:
            async with session.get(f"{base_url}/admin") as response:
                if response.status == 200:
                    print("✅ Admin Panel доступна")
                else:
                    print(f"❌ Admin Panel Failed: {response.status}")
        except Exception as e:
            print(f"❌ Admin Panel Error: {e}")
        
        # 4. Webhook Test
        print("\n4️⃣ Тестируем Webhook...")
        test_data = {
            "type": "message",
            "user_id": "test_user_123",
            "text": "/start"
        }
        
        try:
            async with session.post(f"{base_url}/webhook", json=test_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Webhook OK: {result['status']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Webhook Failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Webhook Error: {e}")
        
        # 5. API Stats
        print("\n5️⃣ Тестируем API Stats...")
        try:
            async with session.get(f"{base_url}/api/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API Stats OK: {data}")
                else:
                    print(f"❌ API Stats Failed: {response.status}")
        except Exception as e:
            print(f"❌ API Stats Error: {e}")
    
    print("\n🎉 Тестирование завершено!")
    print("\n📋 Следующие шаги:")
    print("1. Откройте админ панель Express.ms")
    print("2. Добавьте бота как SmartApp")
    print("3. Укажите webhook URL")
    print("4. Протестируйте команду /start")

if __name__ == "__main__":
    asyncio.run(test_all_components())


