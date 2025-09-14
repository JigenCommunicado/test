#!/usr/bin/env python3
"""
Скрипт для настройки Cloudflare туннеля для Express Bot
"""

import subprocess
import time
import json
import re
import os

def get_tunnel_url():
    """Получение URL туннеля"""
    try:
        # Запускаем cloudflared и получаем URL
        process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://localhost:5010'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного для получения URL
        time.sleep(5)
        
        # Читаем вывод
        stdout, stderr = process.communicate(timeout=10)
        
        # Ищем URL в выводе
        url_pattern = r'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
        match = re.search(url_pattern, stdout + stderr)
        
        if match:
            tunnel_url = match.group(0)
            print(f"✅ Туннель создан: {tunnel_url}")
            return tunnel_url
        else:
            print("❌ Не удалось получить URL туннеля")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка создания туннеля: {e}")
        return None

def update_config(tunnel_url):
    """Обновление конфигурации с новым URL"""
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

def create_setup_instructions(tunnel_url):
    """Создание инструкций с правильным URL"""
    if not tunnel_url:
        return
    
    instructions = f"""
# 🚀 Express Bot - Готов к настройке в Express.ms

## 📋 Информация о боте:
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Webhook URL**: `{tunnel_url}/webhook`
- **Base URL**: `{tunnel_url}`
- **Admin Panel**: `{tunnel_url}/admin`

## 🔧 Настройка в Express.ms:

### 1. Добавьте бота как SmartApp:
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps" или "Приложения"
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

## 🎯 Ожидаемый результат:
После настройки бот должен:
- Показывать статус "онлайн" в Express.ms
- Отвечать на команду `/start`
- Позволять подавать заявки на рейсы
- Отображать статистику в админ панели
"""
    
    with open('/root/test/express_bot/FINAL_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Инструкции созданы: FINAL_SETUP_GUIDE.md")

def main():
    """Основная функция"""
    print("🚀 Настройка Cloudflare туннеля для Express Bot...")
    
    # 1. Создаем туннель
    print("\n1️⃣ Создаем Cloudflare туннель...")
    tunnel_url = get_tunnel_url()
    
    if tunnel_url:
        # 2. Обновляем конфигурацию
        print("\n2️⃣ Обновляем конфигурацию...")
        config_updated = update_config(tunnel_url)
        
        # 3. Создаем инструкции
        print("\n3️⃣ Создаем инструкции...")
        create_setup_instructions(tunnel_url)
        
        print("\n🎉 Настройка завершена!")
        print(f"📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99")
        print(f"🌐 Webhook URL: {tunnel_url}/webhook")
        print(f"👨‍💼 Admin Panel: {tunnel_url}/admin")
        print(f"📖 Инструкции: FINAL_SETUP_GUIDE.md")
        
        print("\n📋 Следующие шаги:")
        print("1. Откройте админ панель Express.ms")
        print("2. Добавьте бота как SmartApp")
        print("3. Укажите webhook URL")
        print("4. Протестируйте команду /start")
        
    else:
        print("\n❌ Не удалось создать туннель")
        print("📋 Рекомендации:")
        print("1. Проверьте, что cloudflared установлен")
        print("2. Убедитесь, что бот запущен на порту 5010")
        print("3. Попробуйте запустить туннель вручную")

if __name__ == "__main__":
    main()


