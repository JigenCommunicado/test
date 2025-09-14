#!/usr/bin/env python3
"""
Скрипт для настройки и регистрации бота в Express.ms
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

class ExpressBotSetup:
    """Настройка бота для Express.ms"""
    
    def __init__(self):
        self.bot_id = "00c46d64-1127-5a96-812d-3d8b27c58b99"
        self.secret_key = "a75b4cd97d9e88e543f077178b2d5a4f"
        self.webhook_url = "https://comparing-doom-solving-royalty.trycloudflare.com/webhook"
        self.api_base_url = "https://api.express.ms"
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
    
    async def test_connection(self) -> bool:
        """Тестирование подключения к Express.ms API"""
        try:
            await self.create_session()
            logger.info("🔍 Тестируем подключение к Express.ms API...")
            
            # Пробуем разные возможные endpoints
            endpoints = [
                f"{self.api_base_url}/v1/health",
                f"{self.api_base_url}/health",
                f"{self.api_base_url}/status",
                f"https://express.ms/api/v1/health",
                f"https://express.ms/health"
            ]
            
            for endpoint in endpoints:
                try:
                    async with self.session.get(endpoint) as response:
                        logger.info(f"✅ Endpoint {endpoint} доступен: {response.status}")
                        if response.status == 200:
                            text = await response.text()
                            logger.info(f"Ответ: {text[:200]}...")
                            return True
                except Exception as e:
                    logger.warning(f"❌ Endpoint {endpoint} недоступен: {e}")
                    continue
            
            logger.error("❌ Все endpoints недоступны")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования подключения: {e}")
            return False
    
    async def register_bot(self) -> bool:
        """Регистрация бота в Express.ms"""
        try:
            await self.create_session()
            logger.info("📝 Регистрируем бота в Express.ms...")
            
            # Данные для регистрации бота
            bot_data = {
                "bot_id": self.bot_id,
                "name": "Flight Booking Bot",
                "description": "Бот для подачи заявок на командировочные рейсы",
                "webhook_url": self.webhook_url,
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
                "manifest": {
                    "name": "Flight Booking Bot",
                    "version": "1.0.0",
                    "description": "Бот для подачи заявок на командировочные рейсы",
                    "icon": "✈️",
                    "color": "#0088cc",
                    "author": "Express Bot Team"
                }
            }
            
            # Пробуем разные endpoints для регистрации
            register_endpoints = [
                f"{self.api_base_url}/v1/bots/register",
                f"{self.api_base_url}/v1/bots",
                f"{self.api_base_url}/bots/register",
                f"https://express.ms/api/v1/bots/register"
            ]
            
            for endpoint in register_endpoints:
                try:
                    logger.info(f"Пробуем зарегистрировать через {endpoint}...")
                    async with self.session.post(endpoint, json=bot_data) as response:
                        logger.info(f"Ответ {endpoint}: {response.status}")
                        if response.status in [200, 201]:
                            result = await response.json()
                            logger.info(f"✅ Бот успешно зарегистрирован: {result}")
                            return True
                        else:
                            error_text = await response.text()
                            logger.warning(f"❌ Ошибка регистрации через {endpoint}: {response.status} - {error_text}")
                except Exception as e:
                    logger.warning(f"❌ Исключение при регистрации через {endpoint}: {e}")
                    continue
            
            logger.error("❌ Не удалось зарегистрировать бота ни через один endpoint")
            return False
            
        except Exception as e:
            logger.error(f"❌ Исключение при регистрации бота: {e}")
            return False
    
    async def set_webhook(self) -> bool:
        """Установка webhook URL"""
        try:
            await self.create_session()
            logger.info("🔗 Устанавливаем webhook...")
            
            webhook_data = {
                "webhook_url": self.webhook_url,
                "events": [
                    "message",
                    "command", 
                    "callback_query"
                ]
            }
            
            # Пробуем разные endpoints для webhook
            webhook_endpoints = [
                f"{self.api_base_url}/v1/bots/{self.bot_id}/webhook",
                f"{self.api_base_url}/v1/bots/webhook",
                f"{self.api_base_url}/bots/{self.bot_id}/webhook"
            ]
            
            for endpoint in webhook_endpoints:
                try:
                    logger.info(f"Пробуем установить webhook через {endpoint}...")
                    async with self.session.post(endpoint, json=webhook_data) as response:
                        logger.info(f"Ответ {endpoint}: {response.status}")
                        if response.status in [200, 201]:
                            result = await response.json()
                            logger.info(f"✅ Webhook установлен: {result}")
                            return True
                        else:
                            error_text = await response.text()
                            logger.warning(f"❌ Ошибка установки webhook через {endpoint}: {response.status} - {error_text}")
                except Exception as e:
                    logger.warning(f"❌ Исключение при установке webhook через {endpoint}: {e}")
                    continue
            
            logger.error("❌ Не удалось установить webhook ни через один endpoint")
            return False
            
        except Exception as e:
            logger.error(f"❌ Исключение при установке webhook: {e}")
            return False
    
    async def check_bot_status(self) -> dict:
        """Проверка статуса бота"""
        try:
            await self.create_session()
            logger.info("🔍 Проверяем статус бота...")
            
            # Пробуем разные endpoints для проверки статуса
            status_endpoints = [
                f"{self.api_base_url}/v1/bots/{self.bot_id}/status",
                f"{self.api_base_url}/v1/bots/{self.bot_id}",
                f"{self.api_base_url}/bots/{self.bot_id}/status"
            ]
            
            for endpoint in status_endpoints:
                try:
                    logger.info(f"Проверяем статус через {endpoint}...")
                    async with self.session.get(endpoint) as response:
                        logger.info(f"Ответ {endpoint}: {response.status}")
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"✅ Статус получен: {result}")
                            return result
                        else:
                            error_text = await response.text()
                            logger.warning(f"❌ Ошибка получения статуса через {endpoint}: {response.status} - {error_text}")
                except Exception as e:
                    logger.warning(f"❌ Исключение при проверке статуса через {endpoint}: {e}")
                    continue
            
            return {"status": "error", "message": "Не удалось получить статус"}
            
        except Exception as e:
            logger.error(f"❌ Исключение при проверке статуса: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_manifest_file(self) -> bool:
        """Создание файла манифеста для Express.ms"""
        try:
            logger.info("📄 Создаем файл манифеста...")
            
            manifest = {
                "name": "Flight Booking Bot",
                "version": "1.0.0",
                "description": "Бот для подачи заявок на командировочные рейсы",
                "icon": "✈️",
                "color": "#0088cc",
                "author": "Express Bot Team",
                "bot_id": self.bot_id,
                "webhook_url": self.webhook_url,
                "api_url": f"{self.webhook_url.replace('/webhook', '')}/api",
                "manifest_url": f"{self.webhook_url.replace('/webhook', '')}/manifest",
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
            }
            
            with open('/root/test/express_bot/express_bot_manifest.json', 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            logger.info("✅ Файл манифеста создан: express_bot_manifest.json")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания манифеста: {e}")
            return False
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

async def main():
    """Основная функция настройки"""
    logger.info("🚀 Начинаем настройку Express Bot...")
    
    setup = ExpressBotSetup()
    
    try:
        # 1. Тестируем подключение
        logger.info("\n=== ЭТАП 1: ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ ===")
        connection_ok = await setup.test_connection()
        
        # 2. Создаем манифест
        logger.info("\n=== ЭТАП 2: СОЗДАНИЕ МАНИФЕСТА ===")
        manifest_ok = await setup.create_manifest_file()
        
        # 3. Проверяем статус бота
        logger.info("\n=== ЭТАП 3: ПРОВЕРКА СТАТУСА БОТА ===")
        status = await setup.check_bot_status()
        
        # 4. Регистрируем бота
        logger.info("\n=== ЭТАП 4: РЕГИСТРАЦИЯ БОТА ===")
        register_ok = await setup.register_bot()
        
        # 5. Устанавливаем webhook
        logger.info("\n=== ЭТАП 5: УСТАНОВКА WEBHOOK ===")
        webhook_ok = await setup.set_webhook()
        
        # Итоговый отчет
        logger.info("\n" + "="*50)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ:")
        logger.info(f"🔗 Подключение к API: {'✅ OK' if connection_ok else '❌ FAIL'}")
        logger.info(f"📄 Манифест создан: {'✅ OK' if manifest_ok else '❌ FAIL'}")
        logger.info(f"🤖 Регистрация бота: {'✅ OK' if register_ok else '❌ FAIL'}")
        logger.info(f"🔗 Webhook установлен: {'✅ OK' if webhook_ok else '❌ FAIL'}")
        logger.info(f"📱 Bot ID: {setup.bot_id}")
        logger.info(f"🌐 Webhook URL: {setup.webhook_url}")
        logger.info("="*50)
        
        if connection_ok and manifest_ok:
            logger.info("✅ Базовая настройка завершена успешно!")
            logger.info("📋 Следующие шаги:")
            logger.info("1. Загрузите манифест в Express.ms через админ панель")
            logger.info("2. Проверьте статус бота в Express.ms")
            logger.info("3. Протестируйте бота командой /start")
        else:
            logger.warning("⚠️ Некоторые этапы завершились с ошибками")
            logger.info("📋 Рекомендации:")
            logger.info("1. Проверьте правильность Bot ID и Secret Key")
            logger.info("2. Убедитесь, что webhook URL доступен извне")
            logger.info("3. Обратитесь к документации Express.ms")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        await setup.close()

if __name__ == "__main__":
    asyncio.run(main())


