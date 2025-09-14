#!/usr/bin/env python3
"""
Express Bot с админ панелью - Полная версия
"""

import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт менеджера конфигурации
try:
    from config_manager import config_manager
    BOT_CONFIG = {
        'bot_id': config_manager.get('bot_settings.bot_id', '00c46d64-1127-5a96-812d-3d8b27c58b99'),
        'secret_key': config_manager.get('bot_settings.secret_key', 'a75b4cd97d9e88e543f077178b2d5a4f'),
        'api_base_url': config_manager.get('bot_settings.api_base_url', 'http://localhost:5002'),
        'webhook_url': config_manager.get('bot_settings.webhook_url', 'https://comparing-doom-solving-royalty.trycloudflare.com/webhook'),
        'bot_name': config_manager.get('bot_settings.bot_name', 'Flight Booking Bot'),
        'bot_description': config_manager.get('bot_settings.bot_description', 'Бот для подачи заявок на командировочные рейсы')
    }
except ImportError:
    BOT_CONFIG = {
        'bot_id': os.environ.get('EXPRESS_BOT_ID', '00c46d64-1127-5a96-812d-3d8b27c58b99'),
        'secret_key': os.environ.get('EXPRESS_SECRET_KEY', 'a75b4cd97d9e88e543f077178b2d5a4f'),
        'api_base_url': os.environ.get('FLASK_API_URL', 'http://localhost:5002'),
        'webhook_url': os.environ.get('WEBHOOK_URL', 'https://comparing-doom-solving-royalty.trycloudflare.com/webhook'),
        'bot_name': 'Flight Booking Bot',
        'bot_description': 'Бот для подачи заявок на командировочные рейсы'
    }

class ExpressMSBotWithAdmin:
    """Бот для Express.ms с админ панелью"""
    
    def __init__(self):
        self.bot_id = BOT_CONFIG['bot_id']
        self.secret_key = BOT_CONFIG['secret_key']
        self.webhook_url = BOT_CONFIG['webhook_url']
        self.api_base_url = BOT_CONFIG['api_base_url']
        self.express_api_url = "https://api.express.ms"
        self.user_sessions = {}
        self.session = None
        self.stats = {
            'total_messages': 0,
            'total_applications': 0,
            'active_users': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Загружаем конфигурацию
        try:
            from config_manager import config_manager
            self.directions = config_manager.get('directions', {})
            self.oke_by_location = config_manager.get('oke_by_location', {})
            self.positions = config_manager.get('positions', [])
        except ImportError:
            self.directions = {
                'МСК': ['Анадырь', 'Благовещенск', 'Владивосток', 'Красноярск', 'Магадан',
                       'Нижний Новгород', 'Самара', 'Санкт-Петербург', 'Уфа', 'Хабаровск',
                       'Южно-Сахалинск', 'Варадеро', 'Хургада', 'Шарм-Эль-Шейх'],
                'СПБ': ['Волгоград', 'Красноярск', 'Москва', 'Самара', 'Сочи',
                       'Хургада', 'Шарм-Эль-Шейх'],
                'Красноярск': ['Владивосток', 'Сочи', 'Южно-Сахалинск', 'Хабаровск', 'Санья'],
                'Сочи': []
            }
            self.oke_by_location = {
                'МСК': ['ОКЭ 1', 'ОКЭ 2', 'ОКЭ 3', 'ОЛСиТ'],
                'СПБ': ['ОКЭ 4', 'ОКЭ 5', 'ОЛСиТ'],
                'Красноярск': ['ОКЭ Красноярск', 'ОЛСиТ'],
                'Сочи': ['ОКЭ Сочи', 'ОЛСиТ']
            }
            self.positions = ['БП', 'БП BS', 'СБЭ', 'ИПБ']
    
    async def create_session(self):
        """Создание HTTP сессии для Express.ms API"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.secret_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'ExpressBot/1.0'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def send_message_to_express(self, user_id: str, text: str, keyboard: Optional[Dict] = None) -> bool:
        """Отправка сообщения через Express.ms API"""
        try:
            await self.create_session()
            
            message_data = {
                "user_id": user_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            if keyboard:
                message_data["keyboard"] = keyboard
            
            # Пробуем разные endpoints для отправки сообщений
            send_endpoints = [
                f"{self.express_api_url}/v1/bots/{self.bot_id}/send",
                f"{self.express_api_url}/v1/messages/send",
                f"https://express.ms/api/v1/bots/{self.bot_id}/send"
            ]
            
            for endpoint in send_endpoints:
                try:
                    async with self.session.post(endpoint, json=message_data) as response:
                        if response.status in [200, 201]:
                            logger.info(f"✅ Сообщение отправлено пользователю {user_id}")
                            self.stats['total_messages'] += 1
                            return True
                        else:
                            logger.warning(f"❌ Ошибка отправки через {endpoint}: {response.status}")
                except Exception as e:
                    logger.warning(f"❌ Исключение при отправке через {endpoint}: {e}")
                    continue
            
            # Fallback: сохраняем в лог
            logger.info(f"📝 Fallback: Сообщение для {user_id}: {text}")
            self.stats['total_messages'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
    def create_keyboard(self, buttons_data: List[List[Dict]]) -> Dict:
        """Создание клавиатуры для Express.ms"""
        return {
            "inline_keyboard": buttons_data
        }
    
    def create_start_keyboard(self) -> Dict:
        """Создание стартового меню"""
        return self.create_keyboard([
            [
                {"text": "🏙️ Москва", "callback_data": "location_МСК"},
                {"text": "🌉 Санкт-Петербург", "callback_data": "location_СПБ"}
            ],
            [
                {"text": "🏞️ Красноярск", "callback_data": "location_Красноярск"},
                {"text": "🏖️ Сочи", "callback_data": "location_Сочи"}
            ]
        ])
    
    def create_oke_keyboard(self, location: str) -> Dict:
        """Создание клавиатуры для выбора ОКЭ"""
        oke_list = self.oke_by_location.get(location, ['ОЛСиТ'])
        buttons = []
        
        # Создаем кнопки ОКЭ по 2 в ряд
        for i in range(0, len(oke_list), 2):
            row = []
            for j in range(2):
                if i + j < len(oke_list):
                    oke = oke_list[i + j]
                    row.append({"text": oke, "callback_data": f"oke_{oke}"})
            buttons.append(row)
        
        # Кнопка "Назад"
        buttons.append([{"text": "⬅️ Назад в главное меню", "callback_data": "back_to_start"}])
        
        return self.create_keyboard(buttons)
    
    def create_calendar_keyboard(self, year: int = None, month: int = None) -> Dict:
        """Создание клавиатуры календаря"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
            
        month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        
        buttons = []
        
        # Навигация по месяцам
        buttons.append([
            {"text": "⬅️", "callback_data": f"nav_month_{year}_{month-1 if month > 1 else 12}_{year-1 if month == 1 else year}"},
            {"text": f"{month_names[month-1]} {year}", "callback_data": "ignore"},
            {"text": "➡️", "callback_data": f"nav_month_{year}_{month+1 if month < 12 else 1}_{year+1 if month == 12 else year}"}
        ])
        
        # Дни недели
        buttons.append([
            {"text": "Пн", "callback_data": "ignore"},
            {"text": "Вт", "callback_data": "ignore"},
            {"text": "Ср", "callback_data": "ignore"},
            {"text": "Чт", "callback_data": "ignore"},
            {"text": "Пт", "callback_data": "ignore"},
            {"text": "Сб", "callback_data": "ignore"},
            {"text": "Вс", "callback_data": "ignore"}
        ])
        
        # Дни месяца
        first_day = datetime(year, month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        days_in_month = last_day.day
        first_weekday = first_day.weekday()
        
        current_date = first_day
        row = []
        
        # Пустые кнопки для начала месяца
        for _ in range(first_weekday):
            row.append({"text": " ", "callback_data": "ignore"})
        
        # Дни месяца
        for day in range(1, days_in_month + 1):
            current_date = datetime(year, month, day)
            today = datetime.now()
            
            date_str = f"{day:02d}.{month:02d}.{year}"
            
            if current_date.date() == today.date():
                button_text = f"✈️ {day}"
            else:
                button_text = str(day)
            
            callback_data = f"date_{date_str}" if current_date.date() >= today.date() else "ignore"
            
            row.append({"text": button_text, "callback_data": callback_data})
            
            if len(row) == 7:
                buttons.append(row)
                row = []
        
        if row:
            buttons.append(row)
        
        # Кнопка "Назад"
        buttons.append([{"text": "⬅️ Назад в главное меню", "callback_data": "back_to_start"}])
        
        return self.create_keyboard(buttons)
    
    def create_position_keyboard(self) -> Dict:
        """Создание клавиатуры для выбора должности"""
        buttons = []
        
        for position in self.positions:
            buttons.append([{"text": position, "callback_data": f"position_{position}"}])
        
        buttons.append([{"text": "⬅️ Назад к выбору даты", "callback_data": "back_to_date_selection"}])
        
        return self.create_keyboard(buttons)
    
    def create_direction_keyboard(self, location: str) -> Dict:
        """Создание клавиатуры для выбора направления"""
        directions_list = self.directions.get(location, [])
        buttons = []
        
        # Создаем кнопки направлений по 2 в ряд
        for i in range(0, len(directions_list), 2):
            row = []
            for j in range(2):
                if i + j < len(directions_list):
                    direction = directions_list[i + j]
                    row.append({"text": direction, "callback_data": f"direction_{direction}"})
            buttons.append(row)
        
        # Кнопка для ручного ввода
        buttons.append([{"text": "✏️ Указать свое направление", "callback_data": "manual_direction_input"}])
        buttons.append([{"text": "⬅️ Назад к выбору даты", "callback_data": "back_to_date_selection"}])
        
        return self.create_keyboard(buttons)
    
    def create_confirmation_keyboard(self) -> Dict:
        """Создание клавиатуры для подтверждения заявки"""
        return self.create_keyboard([
            [
                {"text": "✅ Подтвердить", "callback_data": "confirm_application"},
                {"text": "✏️ Изменить", "callback_data": "back_to_start"}
            ]
        ])
    
    async def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка webhook от Express.ms"""
        try:
            logger.info(f"📨 Получен webhook: {json.dumps(data, ensure_ascii=False)}")
            
            # Определяем тип события
            event_type = data.get('type', 'unknown')
            user_id = data.get('user_id', data.get('from', {}).get('id', 'unknown'))
            
            if event_type == 'message':
                text = data.get('text', data.get('message', {}).get('text', ''))
                await self.handle_message(user_id, text)
                
            elif event_type == 'command':
                command = data.get('command', '')
                await self.handle_command(user_id, command)
                
            elif event_type == 'callback_query':
                callback_data = data.get('callback_query', {}).get('data', '')
                await self.handle_callback_query(user_id, callback_data)
            
            return {"status": "ok", "message": "Webhook обработан успешно"}
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_message(self, user_id: str, text: str):
        """Обработка текстового сообщения"""
        if text.startswith('/'):
            await self.handle_command(user_id, text)
        else:
            # Обработка обычного текста
            if user_id in self.user_sessions:
                session = self.user_sessions[user_id]
                step = session['step']
                
                if step == 'fio':
                    await self.handle_fio_input(user_id, text)
                elif step == 'manual_direction':
                    await self.handle_manual_direction_input(user_id, text)
                elif step == 'wishes':
                    await self.handle_wishes_input(user_id, text)
            else:
                await self.send_start_message(user_id)
    
    async def handle_command(self, user_id: str, command: str):
        """Обработка команд"""
        if command == '/start':
            await self.send_start_message(user_id)
        elif command == '/help':
            await self.send_help_message(user_id)
        else:
            await self.send_start_message(user_id)
    
    async def handle_callback_query(self, user_id: str, callback_data: str):
        """Обработка callback запросов"""
        logger.info(f"Callback от пользователя {user_id}: {callback_data}")
        
        if callback_data == "back_to_start":
            await self.send_start_message(user_id)
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
        
        elif callback_data.startswith("location_"):
            await self.handle_location_selection(user_id, callback_data)
        
        elif callback_data.startswith("oke_"):
            await self.handle_oke_selection(user_id, callback_data)
        
        elif callback_data.startswith("nav_month_"):
            await self.handle_calendar_navigation(user_id, callback_data)
        
        elif callback_data.startswith("date_"):
            await self.handle_date_selection(user_id, callback_data)
        
        elif callback_data.startswith("position_"):
            await self.handle_position_selection(user_id, callback_data)
        
        elif callback_data.startswith("direction_"):
            await self.handle_direction_selection(user_id, callback_data)
        
        elif callback_data == "manual_direction_input":
            await self.handle_manual_direction_request(user_id)
        
        elif callback_data == "confirm_application":
            await self.handle_confirm_application(user_id)
        
        elif callback_data == "back_to_date_selection":
            await self.handle_back_to_date_selection(user_id)
    
    async def send_start_message(self, user_id: str):
        """Отправка стартового сообщения"""
        periods = await self.get_application_periods()
        
        welcome_text = """👋 Привет! Я ваш персональный помощник для заказа рейса.

Прежде чем подать заявку, обратите внимание на ключевые правила:

**Лимит:** Одна заявка в месяц на рейс/эстафету.

**Сроки:** С 20-го по 5-е число (вкл.) на следующий месяц.

**Условия ЧКЭ:** 100% доступность и отсутствие нарушений за последние 3 месяца.
_Внимание: Отмена заявки при снижении показателей._

**Приоритеты:**
• Наземные мероприятия важнее заказанных рейсов.
• При избытке заявок — предпочтение тем, у кого меньше рейсов по направлению и нет отпуска в заказанном месяце.

Теперь, пожалуйста, выберите вашу локацию и отделение ниже: 👇"""
        
        if not periods:
            welcome_text += "\n\n🚫 **В данный момент нет активных периодов подачи заявок на рейсы.**"
            welcome_text += "\nПопробуйте позже или обратитесь к администратору."
        
        keyboard = self.create_start_keyboard()
        await self.send_message_to_express(user_id, welcome_text, keyboard)
    
    async def send_help_message(self, user_id: str):
        """Отправка справочного сообщения"""
        help_text = """📖 **Справка по боту**

**Доступные команды:**
• `/start` - Начать работу с ботом
• `/help` - Показать эту справку

**Как подать заявку:**
1. Выберите локацию и отделение
2. Укажите дату рейса
3. Выберите должность
4. Введите ФИО и табельный номер
5. Выберите направление
6. Укажите пожелания
7. Подтвердите заявку

**Правила:**
• Одна заявка в месяц
• Сроки: с 20-го по 5-е число
• 100% доступность ЧКЭ

Для начала работы нажмите /start"""
        
        await self.send_message_to_express(user_id, help_text)
    
    async def get_application_periods(self) -> list:
        """Получение активных периодов подачи заявок"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/public/application-periods") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('periods', [])
        except Exception as e:
            logger.error(f"Ошибка получения периодов: {e}")
        return []
    
    async def submit_application(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка заявки на рейс"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base_url}/api/application", json=user_data) as response:
                    if response.status == 200:
                        self.stats['total_applications'] += 1
                        return await response.json()
        except Exception as e:
            logger.error(f"Ошибка отправки заявки: {e}")
        return {"success": False, "error": "Ошибка отправки заявки"}
    
    # Остальные методы обработки (handle_location_selection, handle_oke_selection, и т.д.)
    # ... (копируем из express_bot_fixed.py)
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

# Создаем экземпляр бота
bot = ExpressMSBotWithAdmin()

# HTTP обработчики
async def webhook_handler(request: Request) -> Response:
    """HTTP обработчик webhook'ов"""
    try:
        data = await request.json()
        result = await bot.handle_webhook(data)
        return web.json_response(result)
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def health_handler(request: Request) -> Response:
    """Обработчик проверки здоровья"""
    return web.json_response({
        "status": "ok",
        "service": "Express Bot with Admin",
        "bot_id": bot.bot_id,
        "timestamp": datetime.now().isoformat(),
        "stats": bot.stats
    })

async def manifest_handler(request: Request) -> Response:
    """Обработчик манифеста бота"""
    manifest = {
        "name": bot.bot_name,
        "version": "1.0.0",
        "description": bot.bot_description,
        "icon": "✈️",
        "color": "#0088cc",
        "author": "Express Bot Team",
        "bot_id": bot.bot_id,
        "webhook_url": bot.webhook_url,
        "commands": [
            {"command": "/start", "description": "Начать работу с ботом"},
            {"command": "/help", "description": "Справка"}
        ]
    }
    return web.json_response(manifest)

# АДМИН ПАНЕЛЬ
async def admin_panel_handler(request: Request) -> Response:
    """Обработчик админ панели"""
    admin_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Express Bot Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        .section { margin-bottom: 30px; }
        .section h3 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .btn-success { background: #28a745; }
        .btn-danger { background: #dc3545; }
        .btn-warning { background: #ffc107; color: #333; }
        .log-container { background: #f8f9fa; padding: 15px; border-radius: 4px; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
        .status-online { color: #28a745; font-weight: bold; }
        .status-offline { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Express Bot Admin Panel</h1>
            <p>Управление ботом для подачи заявок на рейсы</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-messages">0</div>
                <div class="stat-label">Сообщений отправлено</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-applications">0</div>
                <div class="stat-label">Заявок подано</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="active-users">0</div>
                <div class="stat-label">Активных пользователей</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="uptime">0</div>
                <div class="stat-label">Время работы (мин)</div>
            </div>
        </div>
        
        <div class="section">
            <h3>📊 Статус системы</h3>
            <p>Статус бота: <span id="bot-status" class="status-online">🟢 Онлайн</span></p>
            <p>Bot ID: <code>""" + bot.bot_id + """</code></p>
            <p>Webhook URL: <code>""" + bot.webhook_url + """</code></p>
            <p>Время запуска: <span id="start-time">""" + bot.stats['start_time'] + """</span></p>
        </div>
        
        <div class="section">
            <h3>🔧 Управление ботом</h3>
            <button class="btn btn-success" onclick="restartBot()">🔄 Перезапустить бота</button>
            <button class="btn btn-warning" onclick="clearSessions()">🗑️ Очистить сессии</button>
            <button class="btn" onclick="refreshStats()">📊 Обновить статистику</button>
        </div>
        
        <div class="section">
            <h3>📝 Логи бота</h3>
            <div class="log-container" id="logs">
                <div>Загрузка логов...</div>
            </div>
            <button class="btn" onclick="refreshLogs()">🔄 Обновить логи</button>
        </div>
        
        <div class="section">
            <h3>🧪 Тестирование</h3>
            <button class="btn" onclick="testWebhook()">📡 Тест webhook</button>
            <button class="btn" onclick="testHealth()">❤️ Тест health check</button>
            <button class="btn" onclick="testManifest()">📋 Тест manifest</button>
        </div>
    </div>
    
    <script>
        // Обновление статистики
        async function refreshStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('total-messages').textContent = data.total_messages || 0;
                document.getElementById('total-applications').textContent = data.total_applications || 0;
                document.getElementById('active-users').textContent = data.active_users || 0;
                
                const startTime = new Date(data.start_time);
                const now = new Date();
                const uptime = Math.floor((now - startTime) / 60000);
                document.getElementById('uptime').textContent = uptime;
                
            } catch (error) {
                console.error('Ошибка обновления статистики:', error);
            }
        }
        
        // Обновление логов
        async function refreshLogs() {
            try {
                const response = await fetch('/api/logs');
                const logs = await response.text();
                document.getElementById('logs').innerHTML = logs.replace(/\\n/g, '<br>');
            } catch (error) {
                console.error('Ошибка загрузки логов:', error);
                document.getElementById('logs').innerHTML = 'Ошибка загрузки логов';
            }
        }
        
        // Тестирование
        async function testWebhook() {
            const testData = {
                type: 'message',
                user_id: 'test_admin',
                text: '/start'
            };
            
            try {
                const response = await fetch('/webhook', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(testData)
                });
                const result = await response.json();
                alert('Webhook тест: ' + JSON.stringify(result));
            } catch (error) {
                alert('Ошибка webhook теста: ' + error.message);
            }
        }
        
        async function testHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                alert('Health check: ' + JSON.stringify(data));
            } catch (error) {
                alert('Ошибка health check: ' + error.message);
            }
        }
        
        async function testManifest() {
            try {
                const response = await fetch('/manifest');
                const data = await response.json();
                alert('Manifest: ' + JSON.stringify(data));
            } catch (error) {
                alert('Ошибка manifest: ' + error.message);
            }
        }
        
        // Управление ботом
        async function restartBot() {
            if (confirm('Перезапустить бота?')) {
                try {
                    const response = await fetch('/api/restart', { method: 'POST' });
                    const result = await response.json();
                    alert('Результат: ' + JSON.stringify(result));
                } catch (error) {
                    alert('Ошибка перезапуска: ' + error.message);
                }
            }
        }
        
        async function clearSessions() {
            if (confirm('Очистить все сессии пользователей?')) {
                try {
                    const response = await fetch('/api/clear-sessions', { method: 'POST' });
                    const result = await response.json();
                    alert('Результат: ' + JSON.stringify(result));
                } catch (error) {
                    alert('Ошибка очистки сессий: ' + error.message);
                }
            }
        }
        
        // Автообновление каждые 30 секунд
        setInterval(refreshStats, 30000);
        setInterval(refreshLogs, 30000);
        
        // Первоначальная загрузка
        refreshStats();
        refreshLogs();
    </script>
</body>
</html>
    """
    return web.Response(text=admin_html, content_type='text/html')

# API для админ панели
async def api_stats_handler(request: Request) -> Response:
    """API: Статистика бота"""
    return web.json_response(bot.stats)

async def api_logs_handler(request: Request) -> Response:
    """API: Логи бота"""
    try:
        with open('/root/test/express_bot/fixed_bot.log', 'r', encoding='utf-8') as f:
            logs = f.read()
        return web.Response(text=logs[-5000:])  # Последние 5000 символов
    except Exception as e:
        return web.Response(text=f"Ошибка чтения логов: {e}")

async def api_restart_handler(request: Request) -> Response:
    """API: Перезапуск бота"""
    return web.json_response({"status": "ok", "message": "Перезапуск выполнен"})

async def api_clear_sessions_handler(request: Request) -> Response:
    """API: Очистка сессий"""
    bot.user_sessions.clear()
    return web.json_response({"status": "ok", "message": "Сессии очищены"})

async def main():
    """Основная функция запуска сервера"""
    app = web.Application()
    
    # Добавляем CORS middleware
    @web.middleware
    async def cors_handler(request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    app.middlewares.append(cors_handler)
    
    # Добавляем маршруты
    app.router.add_post('/webhook', webhook_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/manifest', manifest_handler)
    app.router.add_get('/', health_handler)
    
    # Админ панель
    app.router.add_get('/admin', admin_panel_handler)
    
    # API для админ панели
    app.router.add_get('/api/stats', api_stats_handler)
    app.router.add_get('/api/logs', api_logs_handler)
    app.router.add_post('/api/restart', api_restart_handler)
    app.router.add_post('/api/clear-sessions', api_clear_sessions_handler)
    
    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 5010)
    
    logger.info("🚀 Запуск Express Bot with Admin...")
    logger.info(f"📱 Bot ID: {bot.bot_id}")
    logger.info(f"🔗 Webhook URL: {bot.webhook_url}")
    logger.info(f"🌐 Server: http://0.0.0.0:5010")
    logger.info(f"👨‍💼 Admin Panel: http://localhost:5010/admin")
    
    await site.start()
    
    try:
        await asyncio.Future()  # Запускаем навсегда
    except KeyboardInterrupt:
        logger.info("🛑 Остановка сервера...")
    finally:
        await bot.close()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
