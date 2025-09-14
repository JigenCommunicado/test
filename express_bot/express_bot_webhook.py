#!/usr/bin/env python3
"""
Express Bot Webhook Server
Простой HTTP сервер для обработки webhook'ов от Express Messenger
"""

import asyncio
import json
import logging
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response

from express_bot import bot, final_bot
from express_bot_config import get_config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем конфигурацию
config = get_config()

class ExpressBotWebhookServer:
    """HTTP сервер для обработки webhook'ов Express бота"""
    
    def __init__(self):
        self.bot = bot
        self.config = config
        self.logger = logger
        
    async def webhook_handler(self, request: Request) -> Response:
        """Обработчик webhook'ов от Express"""
        try:
            # Получаем данные из запроса
            data = await request.json()
            self.logger.info(f"📨 Получен webhook: {json.dumps(data, ensure_ascii=False)}")
            
            # Здесь должна быть логика обработки webhook'а от Express
            # В зависимости от типа события (message, command, etc.)
            
            # Пока просто возвращаем успешный ответ
            return web.json_response({
                "status": "ok",
                "message": "Webhook обработан успешно"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки webhook: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)
    
    async def health_handler(self, request: Request) -> Response:
        """Обработчик проверки здоровья сервера"""
        return web.json_response({
            "status": "ok",
            "service": "Express Bot Webhook Server",
            "bot_id": self.config['bot_id'],
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def manifest_handler(self, request: Request) -> Response:
        """Обработчик манифеста бота"""
        manifest = {
            "name": self.config['bot_name'],
            "version": "1.0.0",
            "description": self.config['bot_description'],
            "icon": "✈️",
            "color": "#0088cc",
            "author": "Express Bot Team",
            "webhook": "/webhook",
            "commands": [
                {
                    "command": "/start",
                    "description": "Начать работу с ботом"
                },
                {
                    "command": "/new",
                    "description": "Подать новую заявку на рейс"
                },
                {
                    "command": "/my",
                    "description": "Мои заявки"
                },
                {
                    "command": "/help",
                    "description": "Справка"
                },
                {
                    "command": "/status",
                    "description": "Статус системы"
                }
            ]
        }
        return web.json_response(manifest)
    
    async def admin_panel_handler(self, request: Request) -> Response:
        """Обработчик админ панели"""
        try:
            # Читаем файл админ панели
            admin_panel_path = '/root/test/express_bot/frontend/admin_panel.html'
            with open(admin_panel_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем URL API на правильный
            content = content.replace(
                'const SMARTAPP_URL = \'http://localhost:5002\';',
                f'const SMARTAPP_URL = \'http://{self.config["host"]}:{self.config["port"]}\';'
            )
            
            return web.Response(text=content, content_type='text/html')
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки админ панели: {e}")
            return web.Response(
                text="<h1>Ошибка загрузки админ панели</h1><p>Проверьте логи сервера</p>",
                content_type='text/html',
                status=500
            )
    
    # API обработчики для админ панели
    async def api_login_handler(self, request: Request) -> Response:
        """API: Авторизация"""
        try:
            data = await request.json()
            username = data.get('username')
            password = data.get('password')
            
            # Простая проверка (в реальном проекте нужна база данных)
            if username == 'admin' and password == 'admin':
                return web.json_response({
                    "success": True,
                    "token": "demo_token_123",
                    "user": {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "full_name": "Администратор",
                        "role": "admin",
                        "status": "active",
                        "permissions": ["all"]
                    }
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Неверные учетные данные"
                })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": "Ошибка сервера"
            })
    
    async def api_me_handler(self, request: Request) -> Response:
        """API: Информация о текущем пользователе"""
        return web.json_response({
            "success": True,
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Администратор",
                "role": "admin",
                "status": "active",
                "permissions": ["all"]
            }
        })
    
    async def api_logout_handler(self, request: Request) -> Response:
        """API: Выход из системы"""
        return web.json_response({"success": True})
    
    async def api_users_handler(self, request: Request) -> Response:
        """API: Список пользователей"""
        users = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Администратор",
                "role": "admin",
                "status": "active",
                "created_at": "2025-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "username": "manager1",
                "email": "manager@example.com",
                "full_name": "Менеджер",
                "role": "manager",
                "status": "active",
                "created_at": "2025-01-02T00:00:00Z"
            }
        ]
        return web.json_response({"success": True, "users": users})
    
    async def api_create_user_handler(self, request: Request) -> Response:
        """API: Создание пользователя"""
        try:
            data = await request.json()
            # В реальном проекте здесь была бы запись в базу данных
            return web.json_response({"success": True, "message": "Пользователь создан"})
        except Exception as e:
            return web.json_response({"success": False, "error": "Ошибка создания пользователя"})
    
    async def api_delete_user_handler(self, request: Request) -> Response:
        """API: Удаление пользователя"""
        user_id = request.match_info['user_id']
        return web.json_response({"success": True, "message": f"Пользователь {user_id} удален"})
    
    async def api_schedules_handler(self, request: Request) -> Response:
        """API: Список расписаний уведомлений"""
        schedules = [
            {
                "id": 1,
                "name": "Ежемесячное напоминание",
                "type": "application_reminder",
                "schedule_type": "monthly",
                "is_active": True,
                "next_send": "2025-10-01T09:00:00Z"
            }
        ]
        return web.json_response({"success": True, "schedules": schedules})
    
    async def api_create_schedule_handler(self, request: Request) -> Response:
        """API: Создание расписания уведомлений"""
        try:
            data = await request.json()
            return web.json_response({"success": True, "message": "Расписание создано"})
        except Exception as e:
            return web.json_response({"success": False, "error": "Ошибка создания расписания"})
    
    async def start_server(self):
        """Запуск HTTP сервера"""
        app = web.Application()
        
        # Добавляем CORS middleware
        async def cors_handler(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        app.middlewares.append(cors_handler)
        
        # Добавляем маршруты
        app.router.add_post('/webhook', self.webhook_handler)
        app.router.add_get('/health', self.health_handler)
        app.router.add_get('/manifest', self.manifest_handler)
        app.router.add_get('/', self.health_handler)
        app.router.add_get('/admin', self.admin_panel_handler)
        app.router.add_static('/', path='/root/test/express_bot/frontend', name='static')
        
        # API маршруты для админ панели
        app.router.add_post('/api/auth/login', self.api_login_handler)
        app.router.add_get('/api/auth/me', self.api_me_handler)
        app.router.add_post('/api/auth/logout', self.api_logout_handler)
        app.router.add_get('/api/users', self.api_users_handler)
        app.router.add_post('/api/users', self.api_create_user_handler)
        app.router.add_delete('/api/users/{user_id}', self.api_delete_user_handler)
        app.router.add_get('/api/notifications/schedules', self.api_schedules_handler)
        app.router.add_post('/api/notifications/schedules', self.api_create_schedule_handler)
        
        # Запускаем сервер
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            self.config['host'], 
            self.config['port']
        )
        
        self.logger.info(f"🚀 Запуск Express Bot Webhook Server...")
        self.logger.info(f"📱 Bot ID: {self.config['bot_id']}")
        self.logger.info(f"🔗 Webhook URL: {self.config['webhook_url']}")
        self.logger.info(f"🌐 Server: http://{self.config['host']}:{self.config['port']}")
        
        await site.start()
        
        # Запускаем бота в фоне
        asyncio.create_task(self.bot.startup())
        
        # Ждем завершения
        try:
            await asyncio.Future()  # Запускаем навсегда
        except KeyboardInterrupt:
            self.logger.info("🛑 Остановка сервера...")
        finally:
            await runner.cleanup()

async def main():
    """Основная функция"""
    webhook_server = ExpressBotWebhookServer()
    await webhook_server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
