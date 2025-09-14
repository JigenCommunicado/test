#!/usr/bin/env python3
"""
Настройка ngrok для Express Bot в Docker
"""

import subprocess
import time
import json
import re
import os
import requests
import yaml

def create_env_file():
    """Создание .env файла с переменными окружения"""
    env_content = """# Express Bot Environment Variables
BOT_CREDENTIALS=00c46d64-1127-5a96-812d-3d8b27c58b99:a75b4cd97d9e88e543f077178b2d5a4f
HOST=https://api.express.ms
DATABASE_URL=postgresql://express_bot_user:express_bot_password@postgres:5432/express_bot_db
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=INFO
NGROK_URL=
"""
    
    with open('/root/test/express_bot/.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Создан .env файл с переменными окружения")

def update_ngrok_config(authtoken=None, subdomain=None):
    """Обновление конфигурации ngrok"""
    config = {
        "version": "2",
        "authtoken": authtoken or "# Вставьте ваш ngrok authtoken здесь",
        "tunnels": {
            "express-bot": {
                "proto": "http",
                "addr": "express-bot:8000",
                "inspect": True,
                "bind_tls": True,
                "host_header": "express-bot:8000",
                "web_addr": "0.0.0.0:4040"
            }
        }
    }
    
    if subdomain:
        config["tunnels"]["express-bot"]["subdomain"] = subdomain
    
    with open('/root/test/express_bot/ngrok.yml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print("✅ Конфигурация ngrok обновлена")

def start_docker_services():
    """Запуск Docker сервисов"""
    try:
        print("🐳 Запускаем Docker сервисы...")
        
        # Останавливаем существующие контейнеры
        subprocess.run(["docker-compose", "-f", "docker-compose.ngrok.yml", "down"], 
                      cwd="/root/test/express_bot", check=False)
        
        # Запускаем сервисы
        result = subprocess.run([
            "docker-compose", "-f", "docker-compose.ngrok.yml", "up", "-d"
        ], cwd="/root/test/express_bot", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Docker сервисы запущены")
            return True
        else:
            print(f"❌ Ошибка запуска Docker: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска Docker сервисов: {e}")
        return False

def wait_for_services():
    """Ожидание готовности сервисов"""
    print("⏳ Ожидаем готовности сервисов...")
    
    # Ждем готовности бота
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Бот готов")
                break
        except:
            pass
        time.sleep(2)
    else:
        print("⚠️ Бот не отвечает, продолжаем...")
    
    # Ждем готовности ngrok
    for i in range(30):
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                print("✅ ngrok готов")
                break
        except:
            pass
        time.sleep(2)
    else:
        print("⚠️ ngrok не отвечает, продолжаем...")

def get_ngrok_url():
    """Получение URL ngrok туннеля"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('tunnels'):
                tunnel_url = data['tunnels'][0]['public_url']
                print(f"✅ ngrok туннель: {tunnel_url}")
                return tunnel_url
    except Exception as e:
        print(f"❌ Ошибка получения URL ngrok: {e}")
    
    return None

def update_bot_config(tunnel_url):
    """Обновление конфигурации бота с ngrok URL"""
    if not tunnel_url:
        return False
    
    try:
        # Обновляем .env файл
        env_file = '/root/test/express_bot/.env'
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем NGROK_URL
        content = re.sub(r'NGROK_URL=.*', f'NGROK_URL={tunnel_url}', content)
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ .env файл обновлен: NGROK_URL={tunnel_url}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления конфигурации: {e}")
        return False

def create_docker_instructions(tunnel_url):
    """Создание инструкций для Docker с ngrok"""
    if not tunnel_url:
        return
    
    instructions = f"""
# 🐳 Express Bot с ngrok в Docker - Полная настройка

## 📋 Информация о боте:
- **Bot ID**: `00c46d64-1127-5a96-812d-3d8b27c58b99`
- **Webhook URL**: `{tunnel_url}/webhook`
- **Base URL**: `{tunnel_url}`
- **Health Check**: `{tunnel_url}/health`
- **Stats**: `{tunnel_url}/stats`

## 🐳 Docker сервисы:
- **express-bot**: Основной бот (порт 8000)
- **ngrok**: Туннель (веб-интерфейс: http://localhost:4040)
- **postgres**: База данных (порт 5432)
- **redis**: Кэш (порт 6379)

## ✅ Преимущества Docker + ngrok:
- 🔒 Изолированная среда
- 🚀 Быстрый запуск
- 📊 Веб-интерфейс ngrok: http://localhost:4040
- 🔧 Простое управление
- 📈 Масштабируемость

## 🔧 Настройка в Express.ms:

### 1. Добавьте бота как SmartApp:
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps"
3. Нажмите "Добавить новое приложение"
4. Заполните поля:
   - **Название**: Express Bot Docker
   - **Описание**: Бот для Express.ms в Docker
   - **URL приложения**: `{tunnel_url}`
   - **Webhook URL**: `{tunnel_url}/webhook`
   - **Иконка**: 🐳
   - **Цвет**: #0088cc

### 2. Настройте webhook:
- **Webhook URL**: `{tunnel_url}/webhook`
- **События**: message, command, callback_query
- **Метод**: POST
- **Content-Type**: application/json

## 🧪 Тестирование через API:
```bash
# Health check
curl {tunnel_url}/health

# Manifest
curl {tunnel_url}/manifest

# Stats
curl {tunnel_url}/stats

# Webhook test
curl -X POST {tunnel_url}/webhook \\
  -H "Content-Type: application/json" \\
  -d '{{"type": "message", "user_id": "test", "text": "/start"}}'
```

## 🐳 Управление Docker сервисами:
```bash
# Запуск всех сервисов
docker-compose -f docker-compose.ngrok.yml up -d

# Остановка всех сервисов
docker-compose -f docker-compose.ngrok.yml down

# Просмотр логов
docker-compose -f docker-compose.ngrok.yml logs -f

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose.ngrok.yml logs -f express-bot
docker-compose -f docker-compose.ngrok.yml logs -f ngrok

# Перезапуск сервиса
docker-compose -f docker-compose.ngrok.yml restart express-bot
```

## 📊 Мониторинг:
- **ngrok веб-интерфейс**: http://localhost:4040
- **Статистика бота**: `{tunnel_url}/stats`
- **Health check**: `{tunnel_url}/health`
- **Логи бота**: `docker-compose -f docker-compose.ngrok.yml logs express-bot`
- **Логи ngrok**: `docker-compose -f docker-compose.ngrok.yml logs ngrok`

## 🔧 Устранение проблем:
1. **Бот не запускается**: Проверьте логи `docker-compose logs express-bot`
2. **ngrok не работает**: Проверьте логи `docker-compose logs ngrok`
3. **База данных недоступна**: Проверьте `docker-compose logs postgres`
4. **Redis недоступен**: Проверьте `docker-compose logs redis`

## 📞 Поддержка:
- Логи бота: `docker-compose -f docker-compose.ngrok.yml logs express-bot`
- Конфигурация: `docker-compose.ngrok.yml`
- ngrok веб-интерфейс: http://localhost:4040
- Переменные окружения: `.env`

## 🎯 Ожидаемый результат:
После настройки бот должен:
- Показывать статус "онлайн" в Express.ms
- Отвечать на команду `/start`
- Работать в изолированной Docker среде
- Иметь стабильный ngrok туннель
"""
    
    with open('/root/test/express_bot/DOCKER_NGROK_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Инструкции созданы: DOCKER_NGROK_SETUP_GUIDE.md")

def main():
    """Основная функция"""
    print("🐳 Настройка ngrok для Express Bot в Docker...")
    
    # 1. Создаем .env файл
    print("\n1️⃣ Создаем .env файл...")
    create_env_file()
    
    # 2. Обновляем конфигурацию ngrok
    print("\n2️⃣ Настраиваем ngrok...")
    authtoken = input("Введите ваш ngrok authtoken (или нажмите Enter для пропуска): ").strip()
    subdomain = input("Введите желаемый поддомен (или нажмите Enter для пропуска): ").strip()
    
    update_ngrok_config(authtoken if authtoken else None, subdomain if subdomain else None)
    
    # 3. Запускаем Docker сервисы
    print("\n3️⃣ Запускаем Docker сервисы...")
    if not start_docker_services():
        print("❌ Не удалось запустить Docker сервисы")
        return
    
    # 4. Ждем готовности сервисов
    print("\n4️⃣ Ожидаем готовности сервисов...")
    wait_for_services()
    
    # 5. Получаем URL ngrok
    print("\n5️⃣ Получаем URL ngrok...")
    tunnel_url = get_ngrok_url()
    
    if tunnel_url:
        # 6. Обновляем конфигурацию бота
        print("\n6️⃣ Обновляем конфигурацию бота...")
        update_bot_config(tunnel_url)
        
        # 7. Создаем инструкции
        print("\n7️⃣ Создаем инструкции...")
        create_docker_instructions(tunnel_url)
        
        print("\n🎉 Настройка ngrok для Docker завершена!")
        print(f"🐳 Bot ID: 00c46d64-1127-5a96-812d-3d8b27c58b99")
        print(f"🌐 Webhook URL: {tunnel_url}/webhook")
        print(f"📊 ngrok веб-интерфейс: http://localhost:4040")
        print(f"📖 Инструкции: DOCKER_NGROK_SETUP_GUIDE.md")
        
        print("\n📋 Следующие шаги:")
        print("1. Откройте админ панель Express.ms")
        print("2. Добавьте бота как SmartApp")
        print("3. Укажите webhook URL")
        print("4. Протестируйте команду /start")
        
        print("\n🐳 Docker сервисы работают в фоне")
        print("Для остановки: docker-compose -f docker-compose.ngrok.yml down")
        
    else:
        print("\n❌ Не удалось получить URL ngrok")
        print("📋 Рекомендации:")
        print("1. Проверьте, что Docker сервисы запущены")
        print("2. Убедитесь, что порт 4040 свободен")
        print("3. Проверьте логи: docker-compose -f docker-compose.ngrok.yml logs ngrok")

if __name__ == "__main__":
    main()
