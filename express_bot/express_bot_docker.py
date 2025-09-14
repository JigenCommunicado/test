#!/usr/bin/env python3
"""
Express.ms Bot для Docker развертывания
Согласно официальной документации Express.ms
"""

import os
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

import aiohttp
from aiohttp import web
import asyncpg
import redis.asyncio as redis

# Настройка логирования
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExpressBotDocker:
    """Express.ms Bot для Docker развертывания"""
    
    def __init__(self):
        self.bot_id = None
        self.secret_key = None
        self.host = None
        self.database_url = None
        self.redis_url = None
        
        # Статистика
        self.stats = {
            'messages_received': 0,
            'commands_processed': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat(),
            'last_activity': None
        }
        
        # Подключения
        self.db_pool = None
        self.redis_client = None
        
    async def init_config(self):
        """Инициализация конфигурации из переменных окружения"""
        try:
            # Парсинг BOT_CREDENTIALS
            bot_credentials = os.getenv('BOT_CREDENTIALS', '')
            if ':' in bot_credentials:
                self.bot_id, self.secret_key = bot_credentials.split(':', 1)
            else:
                raise ValueError("BOT_CREDENTIALS должен содержать bot_id:secret_key")
            
            self.host = os.getenv('HOST', 'https://api.express.ms')
            self.database_url = os.getenv('DATABASE_URL')
            self.redis_url = os.getenv('REDIS_URL')
            
            logger.info(f"🤖 Bot ID: {self.bot_id}")
            logger.info(f"🌐 Host: {self.host}")
            logger.info(f"🗄️ Database: {self.database_url}")
            logger.info(f"🔴 Redis: {self.redis_url}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации конфигурации: {e}")
            raise
    
    async def init_database(self):
        """Инициализация подключения к PostgreSQL"""
        if not self.database_url:
            logger.warning("⚠️ DATABASE_URL не указан, пропускаем инициализацию БД")
            return
            
        try:
            self.db_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10
            )
            logger.info("✅ Подключение к PostgreSQL установлено")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise
    
    async def init_redis(self):
        """Инициализация подключения к Redis"""
        if not self.redis_url:
            logger.warning("⚠️ REDIS_URL не указан, пропускаем инициализацию Redis")
            return
            
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("✅ Подключение к Redis установлено")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            raise
    
    async def save_message(self, message_data: Dict[str, Any]):
        """Сохранение сообщения в базу данных"""
        if not self.db_pool:
            return
            
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO messages (user_id, chat_id, message_text, message_type, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                """, 
                message_data.get('user_id'),
                message_data.get('chat_id'),
                message_data.get('text', ''),
                message_data.get('type', 'message'),
                datetime.now()
                )
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения сообщения: {e}")
    
    async def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение данных пользователя из Redis"""
        if not self.redis_client:
            return None
            
        try:
            data = await self.redis_client.get(f"user:{user_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных пользователя: {e}")
            return None
    
    async def save_user_data(self, user_id: str, data: Dict[str, Any]):
        """Сохранение данных пользователя в Redis"""
        if not self.redis_client:
            return
            
        try:
            await self.redis_client.setex(
                f"user:{user_id}",
                3600,  # TTL 1 час
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных пользователя: {e}")
    
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка входящего сообщения"""
        try:
            self.stats['messages_received'] += 1
            self.stats['last_activity'] = datetime.now().isoformat()
            
            user_id = message_data.get('user_id')
            text = message_data.get('text', '').strip()
            
            # Сохранение сообщения
            await self.save_message(message_data)
            
            # Получение данных пользователя
            user_data = await self.get_user_data(user_id) or {}
            
            # Обработка команд
            if text.startswith('/'):
                self.stats['commands_processed'] += 1
                return await self.process_command(text, user_id, user_data)
            
            # Обработка обычных сообщений
            return await self.process_text_message(text, user_id, user_data)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            self.stats['errors'] += 1
            return {"status": "error", "message": "Внутренняя ошибка бота"}
    
    async def process_command(self, command: str, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка команд"""
        if command == '/start':
            await self.save_user_data(user_id, {"state": "started", "step": "welcome"})
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": "👋 Добро пожаловать в Express Bot!\n\nДоступные команды:\n/help - помощь\n/status - статус бота\n/info - информация"
                }
            }
        
        elif command == '/help':
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": "📚 Помощь по командам:\n\n/start - начать работу\n/help - эта справка\n/status - статус бота\n/info - информация о боте"
                }
            }
        
        elif command == '/status':
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": f"📊 Статус бота:\n\n✅ Онлайн\n🤖 ID: {self.bot_id}\n📈 Сообщений: {self.stats['messages_received']}\n⚡ Команд: {self.stats['commands_processed']}\n❌ Ошибок: {self.stats['errors']}"
                }
            }
        
        elif command == '/info':
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": f"ℹ️ Информация о боте:\n\n🏢 Express.ms Bot\n🐳 Docker версия\n🕐 Запущен: {self.stats['start_time']}\n🌐 Host: {self.host}"
                }
            }
        
        else:
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": f"❓ Неизвестная команда: {command}\n\nИспользуйте /help для списка команд"
                }
            }
    
    async def process_text_message(self, text: str, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка текстовых сообщений"""
        # Простая обработка текста
        if "привет" in text.lower():
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": "👋 Привет! Как дела?"
                }
            }
        
        elif "как дела" in text.lower():
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": "😊 Всё отлично! А у вас как?"
                }
            }
        
        else:
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "text": f"Вы написали: {text}\n\nИспользуйте /help для списка команд"
                }
            }
    
    async def webhook_handler(self, request):
        """Обработчик webhook от Express.ms"""
        try:
            data = await request.json()
            logger.info(f"📨 Получено сообщение: {data}")
            
            # Обработка сообщения
            result = await self.process_message(data)
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"❌ Ошибка webhook: {e}")
            self.stats['errors'] += 1
            return web.json_response(
                {"status": "error", "message": "Ошибка обработки webhook"},
                status=500
            )
    
    async def health_handler(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "bot_id": self.bot_id,
            "host": self.host,
            "uptime": self.stats['start_time'],
            "stats": self.stats,
            "database": "connected" if self.db_pool else "disconnected",
            "redis": "connected" if self.redis_client else "disconnected"
        })
    
    async def manifest_handler(self, request):
        """Manifest endpoint для Express.ms"""
        return web.json_response({
            "name": "Express Bot",
            "description": "Бот для Express.ms",
            "version": "1.0.0",
            "bot_id": self.bot_id,
            "capabilities": ["text", "commands"],
            "webhook_url": f"{self.host}/webhook"
        })
    
    async def stats_handler(self, request):
        """Статистика бота"""
        return web.json_response({
            "status": "online",
            "bot_id": self.bot_id,
            "stats": self.stats,
            "timestamp": datetime.now().isoformat()
        })
    
    async def init_app(self):
        """Инициализация приложения"""
        # Инициализация конфигурации
        await self.init_config()
        
        # Инициализация подключений
        await self.init_database()
        await self.init_redis()
        
        # Создание приложения
        app = web.Application()
        
        # Middleware для CORS
        @web.middleware
        async def cors_handler(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        app.middlewares.append(cors_handler)
        
        # Маршруты
        app.router.add_post('/webhook', self.webhook_handler)
        app.router.add_get('/health', self.health_handler)
        app.router.add_get('/manifest', self.manifest_handler)
        app.router.add_get('/stats', self.stats_handler)
        app.router.add_get('/', self.health_handler)
        
        return app
    
    async def start(self):
        """Запуск бота"""
        logger.info("🚀 Запуск Express Bot Docker...")
        
        app = await self.init_app()
        
        # Запуск сервера
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', 8000)
        await site.start()
        
        logger.info("✅ Express Bot Docker запущен на порту 8000")
        logger.info(f"🌐 Health: http://0.0.0.0:8000/health")
        logger.info(f"📋 Manifest: http://0.0.0.0:8000/manifest")
        logger.info(f"📊 Stats: http://0.0.0.0:8000/stats")
        
        # Ожидание
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Остановка бота...")
        finally:
            await runner.cleanup()
            if self.db_pool:
                await self.db_pool.close()
            if self.redis_client:
                await self.redis_client.close()

async def main():
    """Главная функция"""
    bot = ExpressBotDocker()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
