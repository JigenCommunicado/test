#!/usr/bin/env python3
"""
Express Bot с LocalTunnel интеграцией
"""

import asyncio
import aiohttp
import json
import logging
import os
import sys
from datetime import datetime
from aiohttp import web
from config_manager import ConfigManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('localtunnel_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExpressBotLocalTunnel:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.bot_id = self.config_manager.get('bot_settings.bot_id')
        self.secret_key = self.config_manager.get('bot_settings.secret_key')
        self.webhook_url = self.config_manager.get('bot_settings.webhook_url', 'https://express-bot-flight.loca.lt/webhook')
        self.api_base_url = self.config_manager.get('bot_settings.api_base_url', 'https://express-bot-flight.loca.lt')
        
        # Статистика
        self.stats = {
            'messages_received': 0,
            'commands_processed': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat(),
            'last_activity': None
        }
        
        logger.info(f"🤖 Bot ID: {self.bot_id}")
        logger.info(f"🔗 Webhook URL: {self.webhook_url}")
        logger.info(f"🌐 API Base URL: {self.api_base_url}")

    async def handle_webhook(self, request):
        """Обработка webhook от Express.ms"""
        try:
            data = await request.json()
            logger.info(f"📨 Получен webhook: {data}")
            
            self.stats['messages_received'] += 1
            self.stats['last_activity'] = datetime.now().isoformat()
            
            # Обработка разных типов сообщений
            message_type = data.get('type', '')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'command':
                await self.handle_command(data)
            elif message_type == 'callback_query':
                await self.handle_callback(data)
            else:
                logger.info(f"❓ Неизвестный тип сообщения: {message_type}")
            
            return web.json_response({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки webhook: {e}")
            self.stats['errors'] += 1
            return web.json_response({'status': 'error', 'message': str(e)}, status=500)

    async def handle_message(self, data):
        """Обработка обычных сообщений"""
        text = data.get('text', '')
        user_id = data.get('user_id', '')
        
        logger.info(f"💬 Сообщение от {user_id}: {text}")
        
        if text.startswith('/'):
            await self.handle_command(data)
        else:
            # Обычное сообщение - отправляем приветствие
            await self.send_message(user_id, "👋 Привет! Используйте команду /start для начала работы.")

    async def handle_command(self, data):
        """Обработка команд"""
        text = data.get('text', '')
        user_id = data.get('user_id', '')
        
        logger.info(f"⚡ Команда от {user_id}: {text}")
        self.stats['commands_processed'] += 1
        
        if text == '/start':
            await self.send_start_message(user_id)
        elif text == '/help':
            await self.send_help_message(user_id)
        elif text == '/status':
            await self.send_status_message(user_id)
        else:
            await self.send_message(user_id, "❓ Неизвестная команда. Используйте /help для списка команд.")

    async def handle_callback(self, data):
        """Обработка callback запросов"""
        callback_data = data.get('callback_data', '')
        user_id = data.get('user_id', '')
        
        logger.info(f"🔘 Callback от {user_id}: {callback_data}")
        
        # Здесь можно добавить обработку кнопок
        await self.send_message(user_id, f"🔘 Обработан callback: {callback_data}")

    async def send_message(self, user_id, text):
        """Отправка сообщения пользователю"""
        try:
            # В реальной реализации здесь будет вызов API Express.ms
            logger.info(f"📤 Отправка сообщения {user_id}: {text}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return False

    async def send_start_message(self, user_id):
        """Отправка приветственного сообщения"""
        message = """
🚀 **Добро пожаловать в Flight Booking Bot!**

Этот бот поможет вам подать заявку на командировочный рейс.

**Доступные команды:**
/start - Начать работу
/help - Помощь
/status - Статус бота

**Для подачи заявки:**
1. Выберите направление
2. Укажите дату
3. Заполните детали
4. Отправьте заявку

Готовы начать? Используйте команду /help для подробной информации.
        """
        await self.send_message(user_id, message)

    async def send_help_message(self, user_id):
        """Отправка справочного сообщения"""
        message = """
📖 **Справка по командам:**

/start - Начать работу с ботом
/help - Показать эту справку
/status - Показать статус бота

**Процесс подачи заявки:**
1. Выберите направление полета
2. Укажите желаемую дату
3. Заполните контактные данные
4. Отправьте заявку на рассмотрение

**Поддерживаемые направления:**
• Москва - Санкт-Петербург
• Москва - Екатеринбург
• Москва - Новосибирск
• И другие...

Если у вас есть вопросы, обратитесь к администратору.
        """
        await self.send_message(user_id, message)

    async def send_status_message(self, user_id):
        """Отправка статуса бота"""
        uptime = datetime.now() - datetime.fromisoformat(self.stats['start_time'])
        message = f"""
📊 **Статус бота:**

🟢 **Статус:** Онлайн
⏰ **Время работы:** {uptime}
📨 **Сообщений получено:** {self.stats['messages_received']}
⚡ **Команд обработано:** {self.stats['commands_processed']}
❌ **Ошибок:** {self.stats['errors']}
🕐 **Последняя активность:** {self.stats['last_activity'] or 'Нет'}

**Webhook URL:** {self.webhook_url}
**API Base URL:** {self.api_base_url}
        """
        await self.send_message(user_id, message)

    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'bot_id': self.bot_id,
            'webhook_url': self.webhook_url,
            'uptime': datetime.now().isoformat(),
            'stats': self.stats
        })

    async def manifest(self, request):
        """Manifest для Express.ms"""
        manifest = {
            "name": self.bot_config.get('bot_name', 'Flight Booking Bot'),
            "description": self.bot_config.get('bot_description', 'Бот для подачи заявок на командировочные рейсы'),
            "version": "1.0.0",
            "bot_id": self.bot_id,
            "webhook_url": self.webhook_url,
            "api_base_url": self.api_base_url,
            "capabilities": [
                "message_handling",
                "command_processing",
                "callback_handling",
                "webhook_support"
            ],
            "commands": [
                {
                    "command": "/start",
                    "description": "Начать работу с ботом"
                },
                {
                    "command": "/help",
                    "description": "Показать справку"
                },
                {
                    "command": "/status",
                    "description": "Показать статус бота"
                }
            ]
        }
        return web.json_response(manifest)

    async def admin_panel(self, request):
        """Админ панель"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Express Bot Admin Panel</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #0088cc; padding-bottom: 20px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0088cc; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #0088cc; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .info {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .endpoint {{ background: #f0f0f0; padding: 10px; border-radius: 5px; font-family: monospace; margin: 5px 0; }}
        .status-online {{ color: #4caf50; font-weight: bold; }}
        .refresh-btn {{ background: #0088cc; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        .refresh-btn:hover {{ background: #006699; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Express Bot Admin Panel</h1>
            <p>Flight Booking Bot - Управление и мониторинг</p>
        </div>
        
        <div class="info">
            <h3>📋 Информация о боте</h3>
            <div class="endpoint"><strong>Bot ID:</strong> {self.bot_id}</div>
            <div class="endpoint"><strong>Webhook URL:</strong> {self.webhook_url}</div>
            <div class="endpoint"><strong>API Base URL:</strong> {self.api_base_url}</div>
            <div class="endpoint"><strong>Статус:</strong> <span class="status-online">🟢 Онлайн</span></div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{self.stats['messages_received']}</div>
                <div class="stat-label">Сообщений получено</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats['commands_processed']}</div>
                <div class="stat-label">Команд обработано</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats['errors']}</div>
                <div class="stat-label">Ошибок</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats['start_time'][:19]}</div>
                <div class="stat-label">Время запуска</div>
            </div>
        </div>
        
        <div class="info">
            <h3>🔧 Endpoints</h3>
            <div class="endpoint">GET /health - Health check</div>
            <div class="endpoint">GET /manifest - Manifest для Express.ms</div>
            <div class="endpoint">POST /webhook - Webhook от Express.ms</div>
            <div class="endpoint">GET /admin - Админ панель</div>
            <div class="endpoint">GET /api/stats - API статистики</div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="refresh-btn" onclick="location.reload()">🔄 Обновить</button>
        </div>
    </div>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')

    async def api_stats(self, request):
        """API статистики"""
        return web.json_response({
            'bot_id': self.bot_id,
            'status': 'online',
            'stats': self.stats,
            'webhook_url': self.webhook_url,
            'api_base_url': self.api_base_url,
            'timestamp': datetime.now().isoformat()
        })

    async def create_app(self):
        """Создание веб-приложения"""
        app = web.Application()
        
        # CORS middleware
        @web.middleware
        async def cors_handler(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        app.middlewares.append(cors_handler)
        
        # Routes
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/manifest', self.manifest)
        app.router.add_post('/webhook', self.handle_webhook)
        app.router.add_get('/admin', self.admin_panel)
        app.router.add_get('/api/stats', self.api_stats)
        
        return app

async def main():
    """Основная функция"""
    try:
        # Создаем бота
        bot = ExpressBotLocalTunnel()
        
        # Создаем приложение
        app = await bot.create_app()
        
        # Запускаем сервер
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Используем порт 5011 вместо 5010
        site = web.TCPSite(runner, '0.0.0.0', 5011)
        
        logger.info("🚀 Запуск Express Bot с LocalTunnel...")
        logger.info(f"📱 Bot ID: {bot.bot_id}")
        logger.info(f"🔗 Webhook URL: {bot.webhook_url}")
        logger.info(f"🌐 Server: http://0.0.0.0:5011")
        logger.info(f"👨‍💼 Admin Panel: http://localhost:5011/admin")
        logger.info(f"🌐 LocalTunnel: https://express-bot-flight.loca.lt")
        
        await site.start()
        
        # Ждем завершения
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал завершения...")
        finally:
            await runner.cleanup()
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
