#!/usr/bin/env python3
"""
Тест заявок
"""

import requests
import json

def test_applications():
    print("🔍 Тестирование заявок...")
    
    try:
        response = requests.get('http://localhost:8082/api/applications')
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Успех: {data.get('success')}")
            print(f"Всего заявок: {data.get('total', 0)}")
            
            if data.get('applications'):
                print("📋 Заявки:")
                for i, app in enumerate(data['applications']):
                    print(f"  {i+1}. {app.get('full_name')} - {app.get('direction')}")
            else:
                print("⚠️  Заявки не найдены")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_applications()
