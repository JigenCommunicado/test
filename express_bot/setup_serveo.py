#!/usr/bin/env python3
"""
Настройка Serveo для Express Bot (бесплатная альтернатива ngrok)
"""

import subprocess
import time
import json
import re
import os
import requests

def start_serveo_tunnel():
    """Запуск Serveo туннеля"""
    try:
        print("🚀 Запускаем Serveo туннель...")
        
        # Запускаем Serveo в фоне
        process = subprocess.Popen(
            ["ssh", "-R", "80:localhost:5010", "serveo.net"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска
        time.sleep(5)
        
        # Парсим вывод для получения URL
        stdout, stderr = process.communicate(timeout=10)
        
        # Ищем URL в выводе
        url_pattern = r'https://[a-zA-Z0-9-]+\.serveo\.net'
        match = re.search(url_pattern, stdout + stderr)
        
        if match:
            tunnel_url = match.group(0)
            print(f"✅ Serveo туннель создан: {tunnel_url}")
            return tunnel_url, process
        else:
            print("❌ Не удалось получить URL туннеля")
            print(f"Вывод: {stdout}")
            print(f"Ошибки: {stderr}")
            return None, process
            
    except Exception as e:
        print(f"❌ Ошибка создания туннеля: {e}")
        return None, None

def update_config_with_serveo(tunnel_url):
    """Обновление конфигурации с Serveo URL"""
    if not tunnel_url:
        return False
    
    try:
        # Читаем текущую конфигурацию
        with open('/root/test/express_bot/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Обновляем webhook URL
        config['bot_settings']['webhook_url'] = f"{tunnel_url}/webhook"
        
        # Сохраняем обновленную конфигурацию
        with open('/root/test/express_bot/config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Конфигурация обновлена: {tunnel_url}/webhook")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления конфигурации: {e}")
        return False

def test_tunnel(tunnel_url):
    """Тестирование туннеля"""
    try:
        print(f"🧪 Тестируем туннель: {tunnel_url}")
        
        # Тестируем health check
        response = requests.get(f"{tunnel_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check прошел")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования туннеля: {e}")
        return False

def create_serveo_instructions(tunnel_url):
    """Создание инструкций с Serveo URL"""
    if not tunnel_url:
        return
    
    instructions = f"""
# 🚀 Express Bot с Serveo - Бесплатная настройка

## 📋 Информация о боте:
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Webhook URL**: `{tunnel_url}/webhook`
- **Base URL**: `{tunnel_url}`
- **Admin Panel**: `{tunnel_url}/admin`

## ✅ Преимущества Serveo:
- 🆓 **Бесплатный** - не требует регистрации
- 🔒 **Стабильный** - SSH-based туннель
- 🚀 **Быстрый** - мгновенный запуск
- 🔧 **Простой** - одна команда

## 🔧 Настройка в Express.ms:

### 1. Добавьте бота как SmartApp:
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Нажмите "Добавить новое приложение"
4. Заполните поля:
   - **Название**: Flight Booking Bot
   - **Описание**: Бот для подачи заявок на командировочные рейсы
   - **URL приложения**: `{tunnel_url}`
   - **Webhook URL**: `{tunnel_url}/webhook`
   - **Иконка**: ✈️
   - **Цвет**: #0088cc

### 2. Настройте webhook:
- **Webhook URL**: `{tunnel_url}/webhook`
- **События**: message, command, callback_query
- **Метод**: POST
- **Content-Type**: application/json

### 3. Тестирование:
1. Сохраните настройки
2. Проверьте статус бота (должен быть "онлайн")
3. Отправьте команду `/start` боту
4. Проверьте админ панель: `{tunnel_url}/admin`

## 🧪 Тестирование через API:
```bash
# Health check
curl {tunnel_url}/health

# Manifest
curl {tunnel_url}/manifest

# Webhook test
curl -X POST {tunnel_url}/webhook \\
  -H "Content-Type: application/json" \\
  -d '{{"type": "message", "user_id": "test", "text": "/start"}}'
```

## 📊 Мониторинг:
- **Админ панель**: `{tunnel_url}/admin`
- **Статистика**: `{tunnel_url}/api/stats`
- **Логи**: `tail -f /root/test/express_bot/fixed_bot.log`

## 🔧 Управление туннелем:
```bash
# Остановить туннель
pkill ssh

# Запустить туннель
ssh -R 80:localhost:5010 serveo.net

# Проверить статус
ps aux | grep serveo
```

## 🎯 Ожидаемый результат:
После настройки бот должен:
- Показывать статус "онлайн" в Express.ms
- Отвечать на команду `/start`
- Позволять подавать заявки на рейсы
- Отображать статистику в админ панели

## 🔧 Устранение проблем:
1. **Бот оффлайн**: Проверьте webhook URL и права доступа
2. **Ошибки webhook**: Проверьте логи бота
3. **Не отвечает**: Проверьте статус сервера и туннеля
4. **Туннель не работает**: Перезапустите Serveo

## 📞 Поддержка:
- Логи бота: `/root/test/express_bot/fixed_bot.log`
- Конфигурация: `/root/test/express_bot/config.json`
- Админ панель: `{tunnel_url}/admin`
"""
    
    with open('/root/test/express_bot/SERVEO_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Инструкции созданы: SERVEO_SETUP_GUIDE.md")

def main():
    """Основная функция"""
    print("🚀 Настройка Serveo для Express Bot...")
    
    # 1. Запускаем туннель
    print("\n1️⃣ Запускаем Serveo туннель...")
    tunnel_url, process = start_serveo_tunnel()
    
    if tunnel_url:
        # 2. Обновляем конфигурацию
        print("\n2️⃣ Обновляем конфигурацию...")
        config_updated = update_config_with_serveo(tunnel_url)
        
        # 3. Тестируем туннель
        print("\n3️⃣ Тестируем туннель...")
        test_passed = test_tunnel(tunnel_url)
        
        # 4. Создаем инструкции
        print("\n4️⃣ Создаем инструкции...")
        create_serveo_instructions(tunnel_url)
        
        print("\n🎉 Настройка Serveo завершена!")
        print(f"📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99")
        print(f"🌐 Webhook URL: {tunnel_url}/webhook")
        print(f"👨‍💼 Admin Panel: {tunnel_url}/admin")
        print(f"📖 Инструкции: SERVEO_SETUP_GUIDE.md")
        
        print("\n📋 Следующие шаги:")
        print("1. Откройте админ панель Express.ms")
        print("2. Добавьте бота как SmartApp")
        print("3. Укажите webhook URL")
        print("4. Протестируйте команду /start")
        
        print(f"\n🔧 Туннель работает в фоне (PID: {process.pid})")
        print("Для остановки: pkill ssh")
        
    else:
        print("\n❌ Не удалось создать туннель")
        print("📋 Рекомендации:")
        print("1. Проверьте, что бот запущен на порту 5010")
        print("2. Убедитесь, что SSH доступен")
        print("3. Попробуйте запустить Serveo вручную: ssh -R 80:localhost:5010 serveo.net")

if __name__ == "__main__":
    main()

