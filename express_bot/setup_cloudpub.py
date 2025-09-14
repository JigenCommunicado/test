#!/usr/bin/env python3
"""
Настройка CloudPub для Express Bot
"""

import subprocess
import time
import json
import os
import requests

def install_cloudpub():
    """Установка CloudPub клиента"""
    try:
        print("🚀 Устанавливаем CloudPub...")
        
        # Устанавливаем CloudPub
        cmd = [
            "bash", "-c", 
            'export CLO_VERSION="2.2.2" && '
            'sudo mkdir -p /usr/local/bin && cd /usr/local/bin && '
            'sudo curl -L "https://cloudpub.ru/download/stable/clo-${CLO_VERSION}-stable-linux-$(uname -m).tar.gz" | sudo tar -xzv && '
            'sudo chmod +x clo'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ CloudPub установлен успешно")
            return True
        else:
            print(f"❌ Ошибка установки CloudPub: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка установки CloudPub: {e}")
        return False

def check_cloudpub():
    """Проверка установки CloudPub"""
    try:
        result = subprocess.run(["/usr/local/bin/clo", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ CloudPub установлен: {result.stdout.strip()}")
            return True
        else:
            print("❌ CloudPub не установлен")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки CloudPub: {e}")
        return False

def setup_cloudpub_token():
    """Настройка токена CloudPub"""
    print("\n📋 Для настройки CloudPub нужен токен:")
    print("1. Перейдите на https://cloudpub.ru")
    print("2. Зарегистрируйтесь или войдите в аккаунт")
    print("3. Получите токен в личном кабинете")
    print("4. Выполните команду: sudo -H clo set token <ваш_токен>")
    
    token = input("\nВведите токен CloudPub (или нажмите Enter для пропуска): ").strip()
    
    if token:
        try:
            result = subprocess.run(["/usr/local/bin/clo", "set", "token", token], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Токен CloudPub настроен")
                return True
            else:
                print(f"❌ Ошибка настройки токена: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Ошибка настройки токена: {e}")
            return False
    else:
        print("⚠️ Токен не указан, настройте вручную")
        return False

def register_express_bot():
    """Регистрация Express Bot в CloudPub"""
    try:
        print("📝 Регистрируем Express Bot в CloudPub...")
        
        # Регистрируем HTTP сервис
        cmd = ["/usr/local/bin/clo", "register", "--name", "express-bot", "http", "localhost:5011"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Express Bot зарегистрирован в CloudPub")
            print(f"📋 Вывод: {result.stdout}")
            return True
        else:
            print(f"❌ Ошибка регистрации: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка регистрации Express Bot: {e}")
        return False

def start_cloudpub_service():
    """Запуск сервиса CloudPub"""
    try:
        print("🚀 Запускаем сервис CloudPub...")
        
        # Включаем и запускаем сервис
        subprocess.run(["sudo", "systemctl", "enable", "clo.service"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "clo.service"], check=True)
        
        print("✅ Сервис CloudPub запущен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска сервиса CloudPub: {e}")
        return False

def get_cloudpub_url():
    """Получение URL CloudPub"""
    try:
        print("🔍 Получаем URL CloudPub...")
        
        # Получаем список сервисов
        result = subprocess.run(["/usr/local/bin/clo", "list"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("📋 Сервисы CloudPub:")
            print(result.stdout)
            
            # Ищем URL для express-bot
            lines = result.stdout.split('\n')
            for line in lines:
                if 'express-bot' in line and 'http' in line:
                    # Извлекаем URL
                    parts = line.split()
                    for part in parts:
                        if part.startswith('http'):
                            print(f"🌐 Express Bot URL: {part}")
                            return part
            
            print("⚠️ URL для express-bot не найден")
            return None
        else:
            print(f"❌ Ошибка получения списка сервисов: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка получения URL: {e}")
        return None

def update_config_with_cloudpub(url):
    """Обновление конфигурации с CloudPub URL"""
    if not url:
        return False
    
    try:
        # Читаем текущую конфигурацию
        with open('/root/test/express_bot/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Обновляем URLs
        config['bot_settings']['api_base_url'] = url
        config['bot_settings']['webhook_url'] = f"{url}/webhook"
        
        # Сохраняем обновленную конфигурацию
        with open('/root/test/express_bot/config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Конфигурация обновлена: {url}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления конфигурации: {e}")
        return False

def test_cloudpub_url(url):
    """Тестирование CloudPub URL"""
    if not url:
        return False
    
    try:
        print(f"🧪 Тестируем CloudPub URL: {url}")
        
        # Тестируем health check
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ CloudPub URL работает")
            return True
        else:
            print(f"❌ CloudPub URL не отвечает: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования CloudPub URL: {e}")
        return False

def create_cloudpub_instructions(url):
    """Создание инструкций для CloudPub"""
    instructions = f"""
# 🚀 Express Bot с CloudPub - Российское решение

## 📋 Информация о боте:
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Webhook URL**: `{url}/webhook`
- **Base URL**: `{url}`
- **Admin Panel**: `{url}/admin`

## ✅ Преимущества CloudPub:
- 🇷🇺 **Российский сервис** - быстрый доступ из России
- 🔒 **Безопасный** - защищенное соединение
- 🚀 **Стабильный** - надежная работа
- 🔧 **Простой** - легкая настройка
- 🌐 **Собственные домены** - поддержка кастомных доменов

## 🔧 Настройка в Express.ms:

### 1. Добавьте бота как SmartApp:
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Нажмите "Добавить новое приложение"
4. Заполните поля:
   - **Название**: Flight Booking Bot
   - **Описание**: Бот для подачи заявок на командировочные рейсы
   - **URL приложения**: `{url}`
   - **Webhook URL**: `{url}/webhook`
   - **Иконка**: ✈️
   - **Цвет**: #0088cc

### 2. Настройте webhook:
- **Webhook URL**: `{url}/webhook`
- **События**: message, command, callback_query
- **Метод**: POST
- **Content-Type**: application/json

## 🧪 Тестирование:
```bash
# Health check
curl {url}/health

# Manifest
curl {url}/manifest

# Webhook test
curl -X POST {url}/webhook \\
  -H "Content-Type: application/json" \\
  -d '{{"type": "message", "user_id": "test", "text": "/start"}}'
```

## 🔧 Управление CloudPub:
```bash
# Просмотр сервисов
sudo clo list

# Остановка сервиса
sudo clo stop express-bot

# Запуск сервиса
sudo clo start express-bot

# Удаление сервиса
sudo clo remove express-bot

# Перезапуск сервиса
sudo systemctl restart clo.service
```

## 📊 Мониторинг:
- **Админ панель**: `{url}/admin`
- **Статистика**: `{url}/api/stats`
- **Логи CloudPub**: `sudo journalctl -u clo.service -f`

## 🎯 Ожидаемый результат:
После настройки бот должен:
- Показывать статус "онлайн" в Express.ms
- Отвечать на команду `/start`
- Позволять подавать заявки на рейсы
- Отображать статистику в админ панели

## 🔧 Устранение проблем:
1. **Бот оффлайн**: Проверьте статус CloudPub: `sudo clo list`
2. **Ошибки webhook**: Проверьте логи: `sudo journalctl -u clo.service`
3. **Не отвечает**: Перезапустите сервис: `sudo systemctl restart clo.service`

## 📞 Поддержка:
- **CloudPub**: https://cloudpub.ru
- **Документация**: https://cloudpub.ru/docs
- **Логи бота**: `/root/test/express_bot/localtunnel_bot.log`
"""
    
    with open('/root/test/express_bot/CLOUDPUB_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Инструкции созданы: CLOUDPUB_SETUP_GUIDE.md")

def main():
    """Основная функция"""
    print("🚀 Настройка CloudPub для Express Bot...")
    print("=" * 50)
    
    # 1. Устанавливаем CloudPub
    print("\n1️⃣ Устанавливаем CloudPub...")
    if not install_cloudpub():
        print("❌ Не удалось установить CloudPub")
        return False
    
    # 2. Проверяем установку
    print("\n2️⃣ Проверяем установку...")
    if not check_cloudpub():
        print("❌ CloudPub не установлен")
        return False
    
    # 3. Настраиваем токен
    print("\n3️⃣ Настраиваем токен...")
    setup_cloudpub_token()
    
    # 4. Регистрируем Express Bot
    print("\n4️⃣ Регистрируем Express Bot...")
    if not register_express_bot():
        print("❌ Не удалось зарегистрировать Express Bot")
        return False
    
    # 5. Запускаем сервис
    print("\n5️⃣ Запускаем сервис...")
    if not start_cloudpub_service():
        print("❌ Не удалось запустить сервис")
        return False
    
    # 6. Получаем URL
    print("\n6️⃣ Получаем URL...")
    url = get_cloudpub_url()
    
    if url:
        # 7. Обновляем конфигурацию
        print("\n7️⃣ Обновляем конфигурацию...")
        update_config_with_cloudpub(url)
        
        # 8. Тестируем URL
        print("\n8️⃣ Тестируем URL...")
        test_cloudpub_url(url)
        
        # 9. Создаем инструкции
        print("\n9️⃣ Создаем инструкции...")
        create_cloudpub_instructions(url)
        
        print("\n🎉 Настройка CloudPub завершена!")
        print(f"📱 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99")
        print(f"🌐 Webhook URL: {url}/webhook")
        print(f"👨‍💼 Admin Panel: {url}/admin")
        print(f"📖 Инструкции: CLOUDPUB_SETUP_GUIDE.md")
        
        print("\n📋 Следующие шаги:")
        print("1. Откройте админ панель Express.ms")
        print("2. Добавьте бота как SmartApp")
        print("3. Укажите webhook URL")
        print("4. Протестируйте команду /start")
        
    else:
        print("\n❌ Не удалось получить URL CloudPub")
        print("📋 Рекомендации:")
        print("1. Проверьте, что токен настроен: sudo clo set token <токен>")
        print("2. Проверьте статус сервиса: sudo systemctl status clo.service")
        print("3. Проверьте логи: sudo journalctl -u clo.service")

if __name__ == "__main__":
    main()

