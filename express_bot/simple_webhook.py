#!/usr/bin/env python3
"""
Simple Express Bot Webhook Server
Простой HTTP сервер для обработки webhook'ов от Express Messenger
"""

import asyncio
import json
import logging
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleExpressBotWebhookServer:
    """Простой HTTP сервер для обработки webhook'ов Express бота"""
    
    def __init__(self):
        self.logger = logger
        self.config = {
            "host": "0.0.0.0",
            "port": 5003
        }
        
    async def webhook_handler(self, request: Request) -> Response:
        """Обработчик webhook'ов от Express"""
        try:
            # Получаем данные из запроса
            data = await request.json()
            self.logger.info(f"📨 Получен webhook: {json.dumps(data, ensure_ascii=False)}")
            
            # Обработка различных типов событий
            event_type = data.get('type', 'unknown')
            user_id = data.get('user_id', 'unknown')
            
            if event_type == 'message':
                self.logger.info(f"💬 Сообщение от пользователя {user_id}: {data.get('text', '')}")
            elif event_type == 'command':
                self.logger.info(f"⚡ Команда от пользователя {user_id}: {data.get('command', '')}")
            elif event_type == 'user_joined':
                self.logger.info(f"👤 Пользователь {user_id} присоединился")
            elif event_type == 'user_left':
                self.logger.info(f"👋 Пользователь {user_id} покинул")
            else:
                self.logger.info(f"📋 Событие {event_type} от пользователя {user_id}")
            
            # Возвращаем успешный ответ
            return web.json_response({
                "status": "ok",
                "message": "Webhook обработан успешно",
                "event_type": event_type,
                "user_id": user_id
            })
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки webhook: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)
    
    async def health_check(self, request: Request) -> Response:
        """Проверка здоровья сервера"""
        return web.json_response({
            "status": "ok",
            "service": "Express Bot Webhook Server",
            "version": "1.0.0"
        })
    
    async def start_server(self):
        """Запуск сервера"""
        app = web.Application()
        
        # Добавляем маршруты
        app.router.add_post('/webhook', self.webhook_handler)
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/', self.health_check)
        
        # Запускаем сервер
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.config['host'], self.config['port'])
        await site.start()
        
        self.logger.info(f"🚀 Express Bot Webhook Server запущен на {self.config['host']}:{self.config['port']}")
        self.logger.info(f"📡 Webhook URL: http://{self.config['host']}:{self.config['port']}/webhook")
        self.logger.info(f"❤️ Health check: http://{self.config['host']}:{self.config['port']}/health")
        
        # Ждем завершения
        try:
            await asyncio.Future()  # Запускаем навсегда
        except KeyboardInterrupt:
            self.logger.info("🛑 Остановка сервера...")
        finally:
            await runner.cleanup()

async def main():
    """Главная функция"""
    server = SimpleExpressBotWebhookServer()
    await server.start_server()

if __name__ == '__main__':
    asyncio.run(main())

