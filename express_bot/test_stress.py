#!/usr/bin/env python3
"""
Тест стресс-тестирования
"""

import requests
import json
import time

def test_stress():
    print("🧪 Тестирование стресс-теста...")
    
    # 1. Запускаем стресс-тест
    print("🚀 Запуск стресс-теста...")
    response = requests.post('http://localhost:8082/api/stress-test/start', 
                           json={'test_type': 'applications', 'count': 3, 'delay': 50, 'concurrency': 1})
    
    if response.status_code == 200:
        print("✅ Стресс-тест запущен")
    else:
        print(f"❌ Ошибка запуска: {response.status_code}")
        return
    
    # 2. Ждем завершения
    print("⏳ Ожидание завершения...")
    time.sleep(5)
    
    # 3. Проверяем статус
    print("📊 Проверка статуса...")
    response = requests.get('http://localhost:8082/api/stress-test/status')
    if response.status_code == 200:
        data = response.json()
        print(f"Статус: {data.get('status')}")
        print(f"Выполнено: {data.get('completed')}/{data.get('total')}")
        print(f"Успешно: {data.get('successful')}")
        print(f"Ошибок: {data.get('errors')}")
    
    # 4. Проверяем заявки
    print("📋 Проверка заявок...")
    response = requests.get('http://localhost:8082/api/applications')
    if response.status_code == 200:
        data = response.json()
        print(f"Всего заявок: {data.get('total', 0)}")
        
        if data.get('applications'):
            print("Последние заявки:")
            for i, app in enumerate(data['applications'][:5]):
                print(f"  {i+1}. {app.get('full_name')} - {app.get('direction')} ({app.get('created_at')})")
        else:
            print("⚠️  Заявки не найдены")

if __name__ == "__main__":
    test_stress()
