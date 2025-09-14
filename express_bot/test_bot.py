#!/usr/bin/env python3
"""
Тест исправленного Express бота
"""

import asyncio
import aiohttp
import json
import time

async def test_bot():
    """Тестирование бота"""
    print("🧪 Тестируем исправленный Express Bot...")
    
    # URL бота
    base_url = "http://localhost:5008"
    webhook_url = f"{base_url}/webhook"
    
    # Тестовые данные
    test_webhooks = [
        {
            "type": "message",
            "user_id": "test_user_123",
            "text": "/start"
        },
        {
            "type": "callback_query",
            "user_id": "test_user_123",
            "callback_query": {
                "data": "location_МСК"
            }
        },
        {
            "type": "callback_query",
            "user_id": "test_user_123",
            "callback_query": {
                "data": "oke_ОКЭ 1"
            }
        },
        {
            "type": "callback_query",
            "user_id": "test_user_123", 
            "callback_query": {
                "data": "date_15.09.2025"
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        # 1. Проверяем health check
        print("\n1️⃣ Проверяем health check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check OK: {data}")
        else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # 2. Проверяем manifest
        print("\n2️⃣ Проверяем manifest...")
        try:
            async with session.get(f"{base_url}/manifest") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Manifest OK: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
                    print(f"❌ Manifest failed: {response.status}")
        except Exception as e:
            print(f"❌ Manifest error: {e}")
        
        # 3. Тестируем webhook'и
        print("\n3️⃣ Тестируем webhook'и...")
        for i, webhook_data in enumerate(test_webhooks, 1):
            print(f"\n   Тест {i}: {webhook_data['type']}")
            try:
                async with session.post(webhook_url, json=webhook_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Webhook {i} OK: {result}")
                else:
                        error_text = await response.text()
                        print(f"   ❌ Webhook {i} failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"   ❌ Webhook {i} error: {e}")
            
            # Небольшая пауза между запросами
            await asyncio.sleep(0.5)
    
    print("\n🎉 Тестирование завершено!")

async def main():
    """Основная функция"""
    print("🚀 Запуск тестирования Express Bot...")
    
    # Ждем запуска бота
    print("⏳ Ждем запуска бота (5 сек)...")
    await asyncio.sleep(5)
    
    await test_bot()

if __name__ == "__main__":
    asyncio.run(main())