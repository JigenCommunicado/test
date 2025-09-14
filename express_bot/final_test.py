#!/usr/bin/env python3
"""
Финальный тест связи сайта с Excel
"""

import requests
import json

def test_api():
    print("🔍 Тестирование API заявок...")
    
    try:
        # Тестируем API заявок
        response = requests.get('http://localhost:8082/api/applications')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API отвечает: {data.get('success', False)}")
            print(f"📊 Найдено заявок: {data.get('total', 0)}")
            
            if data.get('applications'):
                print("📋 Заявки:")
                for i, app in enumerate(data['applications'][:3]):  # Показываем первые 3
                    print(f"  {i+1}. {app.get('full_name', 'N/A')} - {app.get('direction', 'N/A')}")
            else:
                print("⚠️  Заявки не найдены")
                
        else:
            print(f"❌ API ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_api()


