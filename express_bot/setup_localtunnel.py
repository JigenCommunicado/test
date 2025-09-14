#!/usr/bin/env python3
"""
Настройка LocalTunnel для Express Bot
"""

import subprocess
import time
import json
import re
import os
import requests
import signal
import sys

def start_localtunnel():
    """Запуск LocalTunnel"""
    try:
        print("🚀 Запускаем LocalTunnel...")
        
        # Запускаем LocalTunnel в фоне
        process = subprocess.Popen(
            ["npx", "localtunnel", "--port", "5010", "--subdomain", "express-bot-flight"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска
        time.sleep(8)
        
        # Парсим вывод для получения URL
        stdout, stderr = process.communicate(timeout=15)
        
        # Ищем URL в выводе
        url_pattern = r'https://[a-zA-Z0-9-]+\.loca\.lt'
        match = re.search(url_pattern, stdout + stderr)
        
        if match:
            tunnel_url = match.group(0)
            print(f"✅ LocalTunnel создан: {tunnel_url}")
            return tunnel_url, process
        else:
            print("❌ Не удалось получить URL туннеля")
            print(f"Вывод: {stdout}")
            print(f"Ошибки: {stderr}")
            return None, process
            
    except Exception as e:
        print(f"❌ Ошибка создания туннеля: {e}")
        return None, None

def update_config_with_localtunnel(tunnel_url):
    """Обновление конфигурации с LocalTunnel URL"""
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
        response = requests.get(f"{tunnel_url}/health", timeout=15)
        if response.status_code == 200:
            print("✅ Health check прошел")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования туннеля: {e}")
        return False

def create_localtunnel_instructions(tunnel_url):
    """Создание инструкций с LocalTunnel URL"""
    if not tunnel_url:
        return
    
    instructions = f"""
# 🚀 Express Bot с LocalTunnel - Бесплатная настройка

## 📋 Информация о боте:
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Webhook URL**: `{tunnel_url}/webhook`
- **Base URL**: `{tunnel_url}`
- **Admin Panel**: `{tunnel_url}/admin`

## ✅ Преимущества LocalTunnel:
- 🆓 **Бесплатный** - не требует регистрации
- 🔒 **Стабильный** - основан на Node.js
- 🚀 **Быстрый** - мгновенный запуск
- 🔧 **Простой** - одна команда
- 🌐 **Фиксированный домен** - express-bot-flight.loca.lt

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
pkill -f localtunnel

# Запустить туннель
npx localtunnel --port 5010 --subdomain express-bot-flight

# Проверить статус
ps aux | grep localtunnel
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
4. **Туннель не работает**: Перезапустите LocalTunnel

## 📞 Поддержка:
- Логи бота: `/root/test/express_bot/fixed_bot.log`
- Конфигурация: `/root/test/express_bot/config.json`
- Админ панель: `{tunnel_url}/admin`
"""
    
    with open('/root/test/express_bot/LOCALTUNNEL_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Инструкции созданы: LOCALTUNNEL_SETUP_GUIDE.md")

def signal_handler(sig, frame):
    """Обработчик сигналов для корректного завершения"""
    print("\n🛑 Получен сигнал завершения...")
    print("🔧 Для остановки туннеля выполните: pkill -f localtunnel")
    sys.exit(0)

def main():
    """Основная функция"""
    print("🚀 Настройка LocalTunnel для Express Bot...")
    
    # Устанавливаем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 1. Запускаем туннель
    print("\n1️⃣ Запускаем LocalTunnel...")
    tunnel_url, process = start_localtunnel()
    
    if tunnel_url:
        # 2. Обновляем конфигурацию
        print("\n2️⃣ Обновляем конфигурацию...")
        config_updated = update_config_with_localtunnel(tunnel_url)
        
        # 3. Тестируем туннель
        print("\n3️⃣ Тестируем туннель...")
        test_passed = test_tunnel(tunnel_url)
        
        # 4. Создаем инструкции
        print("\n4️⃣ Создаем инструкции...")
        create_localtunnel_instructions(tunnel_url)
        
        print("\n🎉 Настройка LocalTunnel завершена!")
        print(f"📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99")
        print(f"🌐 Webhook URL: {tunnel_url}/webhook")
        print(f"👨‍💼 Admin Panel: {tunnel_url}/admin")
        print(f"📖 Инструкции: LOCALTUNNEL_SETUP_GUIDE.md")
        
        print("\n📋 Следующие шаги:")
        print("1. Откройте админ панель Express.ms")
        print("2. Добавьте бота как SmartApp")
        print("3. Укажите webhook URL")
        print("4. Протестируйте команду /start")
        
        print(f"\n🔧 Туннель работает в фоне (PID: {process.pid})")
        print("Для остановки: pkill -f localtunnel")
        
        # Ждем завершения процесса
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал завершения...")
            process.terminate()
            process.wait()
        
    else:
        print("\n❌ Не удалось создать туннель")
        print("📋 Рекомендации:")
        print("1. Проверьте, что бот запущен на порту 5010")
        print("2. Убедитесь, что Node.js и npm установлены")
        print("3. Попробуйте запустить LocalTunnel вручную: npx localtunnel --port 5010")

if __name__ == "__main__":
    main()

