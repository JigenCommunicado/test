#!/usr/bin/env python3
"""
Express Bot Fixed - Исправленная версия с правильной интеграцией Express.ms
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

class ExpressMSBotFixed:
    """Исправленный бот для Express.ms с правильной интеграцией"""
    
    def __init__(self):
        self.bot_id = BOT_CONFIG['bot_id']
        self.secret_key = BOT_CONFIG['secret_key']
        self.webhook_url = BOT_CONFIG['webhook_url']
        self.api_base_url = BOT_CONFIG['api_base_url']
        self.express_api_url = "https://api.express.ms"
        self.user_sessions = {}
        self.session = None
        
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
                            return True
                        else:
                            logger.warning(f"❌ Ошибка отправки через {endpoint}: {response.status}")
                except Exception as e:
                    logger.warning(f"❌ Исключение при отправке через {endpoint}: {e}")
                    continue
            
            # Fallback: сохраняем в лог
            logger.info(f"📝 Fallback: Сообщение для {user_id}: {text}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
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
                        return await response.json()
        except Exception as e:
            logger.error(f"Ошибка отправки заявки: {e}")
        return {"success": False, "error": "Ошибка отправки заявки"}
    
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
    
    async def handle_location_selection(self, user_id: str, callback_data: str):
        """Обработка выбора локации"""
        location = callback_data.replace("location_", "")
        
        self.user_sessions[user_id] = {
            'step': 'oke',
            'data': {'location': location}
        }
        
        keyboard = self.create_oke_keyboard(location)
        text = f"✅ Вы выбрали локацию: **{location}**!\n\n👌 Отлично!\nТеперь выберите ваше **Подразделение** для *{location}*:"
        
        await self.send_message_to_express(user_id, text, keyboard)
    
    async def handle_oke_selection(self, user_id: str, callback_data: str):
        """Обработка выбора ОКЭ"""
        oke = callback_data.replace("oke_", "")
        
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        self.user_sessions[user_id]['data']['oke'] = oke
        self.user_sessions[user_id]['step'] = 'calendar'
        
        keyboard = self.create_calendar_keyboard()
        text = f"✅ Вы выбрали ОКЭ: **{oke}**!\n\n🗓️ Выберите **дату** для рейса:"
        
        await self.send_message_to_express(user_id, text, keyboard)
    
    async def handle_calendar_navigation(self, user_id: str, callback_data: str):
        """Обработка навигации по календарю"""
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        parts = callback_data.split("_")
        year = int(parts[2])
        month = int(parts[3])
        
        keyboard = self.create_calendar_keyboard(year, month)
        text = "🗓️ Выберите **дату** для рейса:"
        
        await self.send_message_to_express(user_id, text, keyboard)
    
    async def handle_date_selection(self, user_id: str, callback_data: str):
        """Обработка выбора даты"""
        date_str = callback_data.replace("date_", "")
        
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        self.user_sessions[user_id]['data']['date'] = date_str
        self.user_sessions[user_id]['step'] = 'position'
        
        keyboard = self.create_position_keyboard()
        text = f"✅ Выбрана дата: **{date_str}**!\n\n👨‍✈️ Выберите вашу **должность**:"
        
        await self.send_message_to_express(user_id, text, keyboard)
    
    async def handle_position_selection(self, user_id: str, callback_data: str):
        """Обработка выбора должности"""
        position = callback_data.replace("position_", "")
        
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        self.user_sessions[user_id]['data']['position'] = position
        self.user_sessions[user_id]['step'] = 'fio'
        
        text = """📝 Отлично!
Теперь введите ваши **ФИО и Табельный номер** одним сообщением, используя следующий формат:
```
ФИО
Табельный номер
```
Например:
```
Соколянский А.В.
119356
```"""
        
        await self.send_message_to_express(user_id, text)
    
    async def handle_fio_input(self, user_id: str, text: str):
        """Обработка ввода ФИО"""
        lines = text.split('\n')
        if len(lines) >= 2:
            fio = lines[0].strip()
            tab_num = lines[1].strip()
            
            self.user_sessions[user_id]['data']['fio'] = fio
            self.user_sessions[user_id]['data']['tab_num'] = tab_num
            self.user_sessions[user_id]['step'] = 'direction'
            
            location = self.user_sessions[user_id]['data']['location']
            keyboard = self.create_direction_keyboard(location)
            text = f"✅ Вы подтвердили ФИО и Табельный номер!\n\n🌍 Выберите **направление** вашего рейса или введите его вручную:"
            
            await self.send_message_to_express(user_id, text, keyboard)
        else:
            error_text = """⚠️ **Ошибка формата!** Пожалуйста, убедитесь, что вы отправили **ФИО и Табельный номер** в отдельных строках.

Пример корректного формата:
```
Соколянский А.В.
119356
```"""
            await self.send_message_to_express(user_id, error_text)
    
    async def handle_direction_selection(self, user_id: str, callback_data: str):
        """Обработка выбора направления"""
        direction = callback_data.replace("direction_", "")
        
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        self.user_sessions[user_id]['data']['direction'] = direction
        self.user_sessions[user_id]['step'] = 'wishes'
        
        text = f"✅ Вы выбрали направление: **{direction}**!\n\n📝 Отлично! Теперь укажите ваши пожелания. Если пожелания отсутствуют, то поставьте прочерк:"
        
        await self.send_message_to_express(user_id, text)
    
    async def handle_manual_direction_request(self, user_id: str):
        """Обработка запроса на ручной ввод направления"""
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        self.user_sessions[user_id]['step'] = 'manual_direction'
        
        text = "📝 Пожалуйста, введите **название направления** текстом:"
        await self.send_message_to_express(user_id, text)
    
    async def handle_manual_direction_input(self, user_id: str, text: str):
        """Обработка ручного ввода направления"""
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        self.user_sessions[user_id]['data']['direction'] = text
        self.user_sessions[user_id]['step'] = 'wishes'
        
        text = f"✅ Вы указали направление: **{text}**!\n\n📝 Отлично! Теперь укажите ваши пожелания. Если пожелания отсутствуют, то поставьте прочерк:"
        await self.send_message_to_express(user_id, text)
    
    async def handle_wishes_input(self, user_id: str, text: str):
        """Обработка ввода пожеланий"""
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        self.user_sessions[user_id]['data']['wishes'] = text
        self.user_sessions[user_id]['step'] = 'confirmation'
        
        # Показываем сводку для подтверждения
        data = self.user_sessions[user_id]['data']
        summary = f"""✨ **Пожалуйста, проверьте вашу заявку перед отправкой:**

Локация: **{data.get('location', 'Не указана')}**
ОКЭ: **{data.get('oke', 'Не указано')}**
Дата: **{data.get('date', 'Не указана')}**
Должность: **{data.get('position', 'Не указана')}**
ФИО: **{data.get('fio', 'Не указано')}**
Табельный номер: **{data.get('tab_num', 'Не указан')}**
Направление: **{data.get('direction', 'Не указано')}**
Пожелания: **{data.get('wishes', 'Не указаны')}**"""
        
        keyboard = self.create_confirmation_keyboard()
        await self.send_message_to_express(user_id, summary, keyboard)
    
    async def handle_confirm_application(self, user_id: str):
        """Обработка подтверждения заявки"""
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        session = self.user_sessions[user_id]
        
        # Показываем индикатор загрузки
        await self.send_message_to_express(user_id, "⌛ Обрабатываю ваш запрос... Пожалуйста, подождите немного.")
        
        # Отправляем заявку
        application_data = {
            **session['data'],
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        result = await self.submit_application(application_data)
        
        if result.get('success'):
            success_text = """🎉 Поздравляем! Ваши данные успешно отправлены и сохранены.

Напоминаем, что заказ рейса — это возможность, а не гарантия его выполнения. Итоговое решение остается за ЦП при обеспечении плана полетов.

Чтобы вернуться в главное меню и начать заново, нажмите /start."""
            
            keyboard = self.create_start_keyboard()
            await self.send_message_to_express(user_id, success_text, keyboard)
        else:
            error_text = f"""❌ **Ошибка при подаче заявки**

Причина: {result.get('error', 'Неизвестная ошибка')}

Попробуйте еще раз с помощью команды /start."""
            
            keyboard = self.create_start_keyboard()
            await self.send_message_to_express(user_id, error_text, keyboard)
        
        # Очищаем сессию
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    async def handle_back_to_date_selection(self, user_id: str):
        """Обработка возврата к выбору даты"""
        if user_id not in self.user_sessions:
            await self.send_start_message(user_id)
            return
        
        # Очищаем данные после выбора даты
        session = self.user_sessions[user_id]
        session['data'] = {
            'location': session['data'].get('location'),
            'oke': session['data'].get('oke')
        }
        session['step'] = 'calendar'
        
        keyboard = self.create_calendar_keyboard()
        text = "🗓️ Выберите **дату** для рейса:"
        await self.send_message_to_express(user_id, text, keyboard)
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

# Создаем экземпляр бота
bot = ExpressMSBotFixed()

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
        "service": "Express Bot Fixed",
        "bot_id": bot.bot_id,
        "timestamp": datetime.now().isoformat()
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

async def main():
    """Основная функция запуска сервера"""
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
    app.router.add_post('/webhook', webhook_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/manifest', manifest_handler)
    app.router.add_get('/', health_handler)
    
    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 5008)
    
    logger.info("🚀 Запуск Express Bot Fixed...")
    logger.info(f"📱 Bot ID: {bot.bot_id}")
    logger.info(f"🔗 Webhook URL: {bot.webhook_url}")
    logger.info(f"🌐 Server: http://0.0.0.0:5008")
    
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
