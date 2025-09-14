#!/usr/bin/env python3
"""
Правильная интеграция с Express.ms API
Создание бота для Express.ms с использованием их REST API
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpressMSBot:
    """Бот для Express.ms с правильной интеграцией"""
    
    def __init__(self, bot_id: str, secret_key: str, webhook_url: str):
        self.bot_id = bot_id
        self.secret_key = secret_key
        self.webhook_url = webhook_url
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
                }
            )
    
    async def register_bot(self) -> bool:
        """Регистрация бота в Express.ms"""
        try:
            await self.create_session()
            
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
                    }
                ]
            }
            
            async with self.session.post(
                f"{self.api_base_url}/v1/bots/register",
                json=bot_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Бот успешно зарегистрирован: {result}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка регистрации бота: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Исключение при регистрации бота: {e}")
            return False
    
    async def check_bot_status(self) -> Dict[str, Any]:
        """Проверка статуса бота"""
        try:
            await self.create_session()
            
            async with self.session.get(
                f"{self.api_base_url}/v1/bots/{self.bot_id}/status"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "status": "error",
                        "message": f"HTTP {response.status}",
                        "online": False
                    }
                    
        except Exception as e:
            logger.error(f"❌ Ошибка проверки статуса: {e}")
            return {
                "status": "error",
                "message": str(e),
                "online": False
            }
    
    async def send_message(self, user_id: str, text: str, keyboard: Optional[Dict] = None) -> bool:
        """Отправка сообщения пользователю"""
        try:
            await self.create_session()
            
            message_data = {
                "user_id": user_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            if keyboard:
                message_data["keyboard"] = keyboard
            
            async with self.session.post(
                f"{self.api_base_url}/v1/bots/{self.bot_id}/send",
                json=message_data
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Сообщение отправлено пользователю {user_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка отправки сообщения: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Исключение при отправке сообщения: {e}")
            return False
    
    async def set_webhook(self) -> bool:
        """Установка webhook URL"""
        try:
            await self.create_session()
            
            webhook_data = {
                "webhook_url": self.webhook_url,
                "events": [
                    "message",
                    "command",
                    "callback_query"
                ]
            }
            
            async with self.session.post(
                f"{self.api_base_url}/v1/bots/{self.bot_id}/webhook",
                json=webhook_data
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Webhook установлен: {self.webhook_url}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка установки webhook: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Исключение при установке webhook: {e}")
            return False
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """Получение информации о боте"""
        try:
            await self.create_session()
            
            async with self.session.get(
                f"{self.api_base_url}/v1/bots/{self.bot_id}"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "status": "error",
                        "message": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о боте: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

async def main():
    """Основная функция для тестирования интеграции"""
    # Конфигурация из вашего проекта
    bot_id = "00c46d64-1127-5a96-812d-3d8b27c58b99"
    secret_key = "a75b4cd97d9e88e543f077178b2d5a4f"
    webhook_url = "https://comparing-doom-solving-royalty.trycloudflare.com/webhook"
    
    bot = ExpressMSBot(bot_id, secret_key, webhook_url)
    
    try:
        print("🔍 Проверяем статус бота...")
        status = await bot.check_bot_status()
        print(f"Статус: {json.dumps(status, ensure_ascii=False, indent=2)}")
        
        print("\n📋 Получаем информацию о боте...")
        info = await bot.get_bot_info()
        print(f"Информация: {json.dumps(info, ensure_ascii=False, indent=2)}")
        
        print("\n🔗 Устанавливаем webhook...")
        webhook_result = await bot.set_webhook()
        print(f"Webhook установлен: {webhook_result}")
        
        print("\n📝 Регистрируем бота...")
        register_result = await bot.register_bot()
        print(f"Бот зарегистрирован: {register_result}")
        
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())


