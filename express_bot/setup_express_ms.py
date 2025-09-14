#!/usr/bin/env python3
"""
Скрипт для настройки бота в Express.ms
"""

import asyncio
import json
import logging
import aiohttp
import sys
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExpressMSSetup:
    """Настройка бота для Express.ms"""
    
    def __init__(self):
        self.bot_id = "00c46d64-1127-5a96-812d-3d8b27c58b99"
        self.secret_key = "a75b4cd97d9e88e543f077178b2d5a4f"
        self.webhook_url = "https://comparing-doom-solving-royalty.trycloudflare.com:5010/webhook"
        self.base_url = "https://comparing-doom-solving-royalty.trycloudflare.com:5010"
        self.session = None
        
    async def create_session(self):
        """Создание HTTP сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.secret_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'ExpressBot/1.0'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def test_bot_connection(self) -> bool:
        """Тестирование подключения к боту"""
        try:
            logger.info("🔍 Тестируем подключение к боту...")
            
            async with aiohttp.ClientSession() as session:
                # Тестируем health check
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Health check OK: {data}")
                        return True
                    else:
                        logger.error(f"❌ Health check failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к боту: {e}")
            return False
    
    async def get_bot_manifest(self) -> dict:
        """Получение манифеста бота"""
        try:
            logger.info("📋 Получаем манифест бота...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/manifest") as response:
                    if response.status == 200:
                        manifest = await response.json()
                        logger.info(f"✅ Манифест получен: {json.dumps(manifest, ensure_ascii=False, indent=2)}")
                        return manifest
                    else:
                        logger.error(f"❌ Ошибка получения манифеста: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"❌ Ошибка получения манифеста: {e}")
            return {}
    
    async def test_webhook(self) -> bool:
        """Тестирование webhook"""
        try:
            logger.info("🧪 Тестируем webhook...")
            
            test_data = {
                "type": "message",
                "user_id": "test_admin_setup",
                "text": "/start"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.webhook_url}", json=test_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Webhook тест OK: {result}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Webhook тест failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования webhook: {e}")
            return False
    
    def create_express_ms_config(self) -> dict:
        """Создание конфигурации для Express.ms"""
        config = {
            "smartapp": {
                "name": "Flight Booking Bot",
                "description": "Бот для подачи заявок на командировочные рейсы",
                "version": "1.0.0",
                "icon": "✈️",
                "color": "#0088cc",
                "author": "Express Bot Team",
                "bot_id": self.bot_id,
                "webhook_url": self.webhook_url,
                "base_url": self.base_url,
                "manifest_url": f"{self.base_url}/manifest",
                "admin_url": f"{self.base_url}/admin",
                "permissions": [
                    "read_messages",
                    "send_messages",
                    "read_user_info",
                    "access_files"
                ],
                "commands": [
                    {
                        "command": "/start",
                        "description": "Начать работу с ботом"
                    },
                    {
                        "command": "/help",
                        "description": "Справка"
                    },
                    {
                        "command": "/new",
                        "description": "Подать новую заявку на рейс"
                    }
                ],
                "endpoints": {
                    "webhook": "/webhook",
                    "health": "/health",
                    "manifest": "/manifest",
                    "admin": "/admin"
                }
            },
            "express_ms_settings": {
                "bot_id": self.bot_id,
                "secret_key": self.secret_key,
                "webhook_url": self.webhook_url,
                "api_base_url": "https://api.express.ms",
                "registration_required": True,
                "webhook_events": [
                    "message",
                    "command",
                    "callback_query"
                ]
            }
        }
        return config
    
    def save_config(self, config: dict) -> bool:
        """Сохранение конфигурации"""
        try:
            with open('/root/test/express_bot/express_ms_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info("✅ Конфигурация сохранена в express_ms_config.json")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения конфигурации: {e}")
            return False
    
    def create_setup_instructions(self) -> str:
        """Создание инструкций по настройке"""
        instructions = f"""
# 🚀 Инструкции по настройке Express Bot в Express.ms

## 📋 Информация о боте:
- **Bot ID**: {self.bot_id}
- **Webhook URL**: {self.webhook_url}
- **Base URL**: {self.base_url}
- **Admin Panel**: {self.base_url}/admin

## 🔧 Шаги настройки в Express.ms:

### 1. Регистрация бота как SmartApp
1. Войдите в админ панель Express.ms
2. Перейдите в раздел "SmartApps" или "Приложения"
3. Нажмите "Добавить новое приложение"
4. Заполните поля:
   - **Название**: Flight Booking Bot
   - **Описание**: Бот для подачи заявок на командировочные рейсы
   - **URL приложения**: {self.base_url}
   - **Webhook URL**: {self.webhook_url}
   - **Иконка**: ✈️
   - **Цвет**: #0088cc

### 2. Настройка webhook
1. В настройках бота укажите:
   - **Webhook URL**: {self.webhook_url}
   - **События**: message, command, callback_query
   - **Метод**: POST
   - **Content-Type**: application/json

### 3. Настройка прав доступа
Убедитесь, что бот имеет права:
- ✅ Чтение сообщений
- ✅ Отправка сообщений
- ✅ Чтение информации о пользователях
- ✅ Доступ к файлам

### 4. Тестирование
1. Сохраните настройки
2. Проверьте статус бота (должен быть "онлайн")
3. Отправьте команду `/start` боту
4. Проверьте админ панель: {self.base_url}/admin

## 🧪 Тестирование через API:
```bash
# Health check
curl {self.base_url}/health

# Manifest
curl {self.base_url}/manifest

# Webhook test
curl -X POST {self.webhook_url} \\
  -H "Content-Type: application/json" \\
  -d '{{"type": "message", "user_id": "test", "text": "/start"}}'
```

## 📊 Мониторинг:
- **Админ панель**: {self.base_url}/admin
- **Логи**: tail -f /root/test/express_bot/fixed_bot.log
- **Статистика**: {self.base_url}/api/stats

## 🔧 Устранение проблем:
1. **Бот оффлайн**: Проверьте webhook URL и права доступа
2. **Ошибки webhook**: Проверьте логи бота
3. **Не отвечает**: Проверьте статус сервера

## 📞 Поддержка:
- Логи бота: /root/test/express_bot/fixed_bot.log
- Конфигурация: /root/test/express_bot/express_ms_config.json
- Админ панель: {self.base_url}/admin
"""
        return instructions
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

async def main():
    """Основная функция настройки"""
    logger.info("🚀 Начинаем настройку Express Bot для Express.ms...")
    
    setup = ExpressMSSetup()
    
    try:
        # 1. Тестируем подключение к боту
        logger.info("\n=== ЭТАП 1: ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ ===")
        connection_ok = await setup.test_bot_connection()
        
        # 2. Получаем манифест
        logger.info("\n=== ЭТАП 2: ПОЛУЧЕНИЕ МАНИФЕСТА ===")
        manifest = await setup.get_bot_manifest()
        
        # 3. Тестируем webhook
        logger.info("\n=== ЭТАП 3: ТЕСТИРОВАНИЕ WEBHOOK ===")
        webhook_ok = await setup.test_webhook()
        
        # 4. Создаем конфигурацию
        logger.info("\n=== ЭТАП 4: СОЗДАНИЕ КОНФИГУРАЦИИ ===")
        config = setup.create_express_ms_config()
        config_saved = setup.save_config(config)
        
        # 5. Создаем инструкции
        logger.info("\n=== ЭТАП 5: СОЗДАНИЕ ИНСТРУКЦИЙ ===")
        instructions = setup.create_setup_instructions()
        
        with open('/root/test/express_bot/EXPRESS_MS_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        # Итоговый отчет
        logger.info("\n" + "="*60)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ НАСТРОЙКИ:")
        logger.info(f"🔗 Подключение к боту: {'✅ OK' if connection_ok else '❌ FAIL'}")
        logger.info(f"📋 Манифест получен: {'✅ OK' if manifest else '❌ FAIL'}")
        logger.info(f"🧪 Webhook тест: {'✅ OK' if webhook_ok else '❌ FAIL'}")
        logger.info(f"💾 Конфигурация сохранена: {'✅ OK' if config_saved else '❌ FAIL'}")
        logger.info("="*60)
        
        logger.info(f"\n📱 Bot ID: {setup.bot_id}")
        logger.info(f"🌐 Webhook URL: {setup.webhook_url}")
        logger.info(f"👨‍💼 Admin Panel: {setup.base_url}/admin")
        logger.info(f"📋 Manifest: {setup.base_url}/manifest")
        
        if connection_ok and webhook_ok:
            logger.info("\n🎉 Бот готов к настройке в Express.ms!")
            logger.info("📋 Следующие шаги:")
            logger.info("1. Откройте админ панель Express.ms")
            logger.info("2. Добавьте бота как SmartApp")
            logger.info("3. Укажите webhook URL")
            logger.info("4. Протестируйте команду /start")
            logger.info(f"\n📖 Подробные инструкции: EXPRESS_MS_SETUP_GUIDE.md")
        else:
            logger.warning("⚠️ Некоторые тесты не прошли")
            logger.info("📋 Рекомендации:")
            logger.info("1. Проверьте, что бот запущен")
            logger.info("2. Убедитесь, что порты доступны")
            logger.info("3. Проверьте логи бота")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        await setup.close()

if __name__ == "__main__":
    asyncio.run(main())


