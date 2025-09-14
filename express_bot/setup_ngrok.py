#!/usr/bin/env python3
"""
Настройка ngrok для Express Bot
"""

import subprocess
import time
import json
import re
import os
import requests

def install_ngrok():
    """Установка ngrok"""
    try:
        print("📦 Устанавливаем ngrok...")
        
        # Скачиваем ngrok
        subprocess.run([
            "wget", "-O", "/tmp/ngrok.zip", 
            "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"
        ], check=True)
        
        # Распаковываем
        subprocess.run(["unzip", "/tmp/ngrok.zip", "-d", "/usr/local/bin/"], check=True)
        
        # Делаем исполняемым
        subprocess.run(["chmod", "+x", "/usr/local/bin/ngrok"], check=True)
        
        print("✅ ngrok установлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка установки ngrok: {e}")
        return False

def start_ngrok_tunnel():
    """Запуск ngrok туннеля"""
    try:
        print("🚀 Запускаем ngrok туннель...")
        
        # Запускаем ngrok в фоне
        process = subprocess.Popen(
            ["ngrok", "http", "5010", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска
        time.sleep(5)
        
        # Получаем URL через API
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('tunnels'):
                    tunnel_url = data['tunnels'][0]['public_url']
                    print(f"✅ ngrok туннель создан: {tunnel_url}")
                    return tunnel_url, process
        except:
            pass
        
        # Fallback - парсим вывод
        stdout, stderr = process.communicate(timeout=10)
        url_pattern = r'https://[a-zA-Z0-9-]+\.ngrok\.io'
        match = re.search(url_pattern, stdout + stderr)
        
        if match:
            tunnel_url = match.group(0)
            print(f"✅ ngrok туннель создан: {tunnel_url}")
            return tunnel_url, process
        else:
            print("❌ Не удалось получить URL туннеля")
            return None, process
            
    except Exception as e:
        print(f"❌ Ошибка создания туннеля: {e}")
        return None, None

def update_config_with_ngrok(tunnel_url):
    """Обновление конфигурации с ngrok URL"""
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

def create_ngrok_instructions(tunnel_url):
    """Создание инструкций с ngrok URL"""
    if not tunnel_url:
        return
    
    instructions = f"""
# 🚀 Express Bot с ngrok - Стабильная настройка

## 📋 Информация о боте:
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Webhook URL**: `{tunnel_url}/webhook`
- **Base URL**: `{tunnel_url}`
- **Admin Panel**: `{tunnel_url}/admin`

## ✅ Преимущества ngrok:
- 🔒 Стабильный туннель
- 🚀 Быстрый запуск
- 📊 Веб-интерфейс мониторинга: http://localhost:4040
- 🔧 Простое управление

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
- **ngrok веб-интерфейс**: http://localhost:4040
- **Статистика**: `{tunnel_url}/api/stats`
- **Логи**: `tail -f /root/test/express_bot/fixed_bot.log`

## 🔧 Управление туннелем:
```bash
# Остановить туннель
pkill ngrok

# Запустить туннель
ngrok http 5010

# Проверить статус
curl http://localhost:4040/api/tunnels
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
4. **Туннель не работает**: Перезапустите ngrok

## 📞 Поддержка:
- Логи бота: `/root/test/express_bot/fixed_bot.log`
- Конфигурация: `/root/test/express_bot/config.json`
- Админ панель: `{tunnel_url}/admin`
- ngrok веб-интерфейс: http://localhost:4040
"""
    
    with open('/root/test/express_bot/NGROK_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Инструкции созданы: NGROK_SETUP_GUIDE.md")

def main():
    """Основная функция"""
    print("🚀 Настройка ngrok для Express Bot...")
    
    # 1. Устанавливаем ngrok
    print("\n1️⃣ Устанавливаем ngrok...")
    if not install_ngrok():
        print("❌ Не удалось установить ngrok")
        return
    
    # 2. Запускаем туннель
    print("\n2️⃣ Запускаем ngrok туннель...")
    tunnel_url, process = start_ngrok_tunnel()
    
    if tunnel_url:
        # 3. Обновляем конфигурацию
        print("\n3️⃣ Обновляем конфигурацию...")
        config_updated = update_config_with_ngrok(tunnel_url)
        
        # 4. Создаем инструкции
        print("\n4️⃣ Создаем инструкции...")
        create_ngrok_instructions(tunnel_url)
        
        print("\n🎉 Настройка ngrok завершена!")
        print(f"📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99")
        print(f"🌐 Webhook URL: {tunnel_url}/webhook")
        print(f"👨‍💼 Admin Panel: {tunnel_url}/admin")
        print(f"📊 ngrok веб-интерфейс: http://localhost:4040")
        print(f"📖 Инструкции: NGROK_SETUP_GUIDE.md")
        
        print("\n📋 Следующие шаги:")
        print("1. Откройте админ панель Express.ms")
        print("2. Добавьте бота как SmartApp")
        print("3. Укажите webhook URL")
        print("4. Протестируйте команду /start")
        
        print(f"\n🔧 Туннель работает в фоне (PID: {process.pid})")
        print("Для остановки: pkill ngrok")
        
    else:
        print("\n❌ Не удалось создать туннель")
        print("📋 Рекомендации:")
        print("1. Проверьте, что бот запущен на порту 5010")
        print("2. Убедитесь, что порт 4040 свободен")
        print("3. Попробуйте запустить ngrok вручную: ngrok http 5010")

if __name__ == "__main__":
    main()


