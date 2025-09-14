#!/usr/bin/env python3
"""
Express Bot для CloudPub - Адаптированная версия для работы с Express.ms
Система подачи заявок на рейсы с полной функциональностью
"""

import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify, render_template_string
import threading
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт менеджера конфигурации
try:
    from config_manager import config_manager
    # Получаем конфигурацию из JSON файла
    BOT_CONFIG = {
        'bot_id': config_manager.get('bot_settings.bot_id', '00c46d64-1127-5a96-812d-3d8b27c58b99'),
        'secret_key': config_manager.get('bot_settings.secret_key', 'a75b4cd97d9e88e543f077178b2d5a4f'),
        'api_base_url': config_manager.get('bot_settings.api_base_url', 'https://loosely-welcoming-grackle.cloudpub.ru'),
        'webhook_url': config_manager.get('bot_settings.webhook_url', 'https://loosely-welcoming-grackle.cloudpub.ru/webhook'),
        'cloudpub_url': config_manager.get('bot_settings.cloudpub_url', 'https://loosely-welcoming-grackle.cloudpub.ru'),
        'bot_name': config_manager.get('bot_settings.bot_name', 'Flight Booking Bot'),
        'bot_description': config_manager.get('bot_settings.bot_description', 'Бот для подачи заявок на командировочные рейсы')
    }
except ImportError:
    # Fallback к старой конфигурации если config_manager недоступен
    BOT_CONFIG = {
        'bot_id': os.environ.get('EXPRESS_BOT_ID', '00c46d64-1127-5a96-812d-3d8b27c58b99'),
        'secret_key': os.environ.get('EXPRESS_SECRET_KEY', 'a75b4cd97d9e88e543f077178b2d5a4f'),
        'api_base_url': os.environ.get('FLASK_API_URL', 'https://loosely-welcoming-grackle.cloudpub.ru'),
        'webhook_url': os.environ.get('WEBHOOK_URL', 'https://loosely-welcoming-grackle.cloudpub.ru/webhook'),
        'cloudpub_url': os.environ.get('CLOUDPUB_URL', 'https://loosely-welcoming-grackle.cloudpub.ru'),
        'bot_name': 'Flight Booking Bot',
        'bot_description': 'Бот для подачи заявок на командировочные рейсы'
    }

# Создаем Flask приложение
app = Flask(__name__)

class CloudPubFlightBookingBot:
    """Класс бота для работы с Express.ms через CloudPub"""
    
    def __init__(self):
        self.api_url = BOT_CONFIG['api_base_url']
        self.webhook_url = BOT_CONFIG['webhook_url']
        self.cloudpub_url = BOT_CONFIG['cloudpub_url']
        self.user_sessions = {}
        self.stats = {
            'total_applications': 0,
            'active_sessions': 0,
            'start_time': datetime.now()
        }
        
        # Загружаем конфигурацию из JSON файла
        try:
            from config_manager import config_manager
            self.directions = config_manager.get('directions', {})
            self.oke_by_location = config_manager.get('oke_by_location', {})
            self.positions = config_manager.get('positions', [])
        except ImportError:
            # Fallback к захардкоженным значениям
            self.directions = {
                'МСК': [
                    'Анадырь', 'Благовещенск', 'Владивосток', 'Красноярск', 'Магадан',
                    'Нижний Новгород', 'Самара', 'Санкт-Петербург', 'Уфа', 'Хабаровск',
                    'Южно-Сахалинск', 'Варадеро', 'Хургада', 'Шарм-Эль-Шейх'
                ],
                'СПБ': [
                    'Волгоград', 'Красноярск', 'Москва', 'Самара', 'Сочи',
                    'Хургада', 'Шарм-Эль-Шейх'
                ],
                'Красноярск': [
                    'Владивосток', 'Сочи', 'Южно-Сахалинск', 'Хабаровск', 'Санья'
                ],
                'Сочи': []
            }
            self.oke_by_location = {
                'МСК': ['ОКЭ 1', 'ОКЭ 2', 'ОКЭ 3', 'ОЛСиТ'],
                'СПБ': ['ОКЭ 4', 'ОКЭ 5', 'ОЛСиТ'],
                'Красноярск': ['ОКЭ Красноярск', 'ОЛСиТ'],
                'Сочи': ['ОКЭ Сочи', 'ОЛСиТ']
            }
            self.positions = ['БП', 'БП BS', 'СБЭ', 'ИПБ']
    
    async def get_application_periods(self) -> list:
        """Получение активных периодов подачи заявок"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/api/public/application-periods") as response:
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
                async with session.post(f"{self.api_url}/api/application", json=user_data) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"Ошибка отправки заявки: {e}")
        return {"success": False, "error": "Ошибка отправки заявки"}
    
    def create_inline_keyboard(self, buttons_data: List[List[Dict[str, str]]]) -> Dict[str, Any]:
        """Создание inline клавиатуры для Express.ms"""
        keyboard = []
        for row in buttons_data:
            keyboard_row = []
            for button in row:
                keyboard_row.append({
                    "text": button["text"],
                    "callback_data": button["callback_data"]
                })
            keyboard.append(keyboard_row)
        
        return {
            "inline_keyboard": keyboard
        }
    
    def create_start_keyboard(self) -> Dict[str, Any]:
        """Создание стартового меню с выбором локации"""
        buttons = [
            [
                {"text": "🏙️ Москва", "callback_data": "location_МСК"},
                {"text": "🌉 Санкт-Петербург", "callback_data": "location_СПБ"}
            ],
            [
                {"text": "🏞️ Красноярск", "callback_data": "location_Красноярск"},
                {"text": "🏖️ Сочи", "callback_data": "location_Сочи"}
            ]
        ]
        return self.create_inline_keyboard(buttons)
    
    def create_oke_keyboard(self, location: str) -> Dict[str, Any]:
        """Создание клавиатуры для выбора ОКЭ"""
        oke_list = self.oke_by_location.get(location, ['ОЛСиТ'])
        buttons = []
        
        # Создаем кнопки ОКЭ (по 2 в ряд)
        for i in range(0, len(oke_list), 2):
            row = []
            for j in range(2):
                if i + j < len(oke_list):
                    oke = oke_list[i + j]
                    row.append({
                        "text": oke,
                        "callback_data": f"oke_{oke}"
                    })
            buttons.append(row)
        
        # Кнопка "Назад в главное меню"
        buttons.append([{"text": "⬅️ Назад в главное меню", "callback_data": "back_to_start"}])
        
        return self.create_inline_keyboard(buttons)
    
    def create_calendar_keyboard(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Создание клавиатуры календаря"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
            
        buttons = []
        
        # Названия месяцев
        month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        
        # Навигация по месяцам
        nav_buttons = [
            {"text": "⬅️", "callback_data": f"nav_month_{year}_{month-1 if month > 1 else 12}_{year-1 if month == 1 else year}"},
            {"text": f"{month_names[month-1]} {year}", "callback_data": "ignore"},
            {"text": "➡️", "callback_data": f"nav_month_{year}_{month+1 if month < 12 else 1}_{year+1 if month == 12 else year}"}
        ]
        buttons.append(nav_buttons)
        
        # Дни недели
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        weekdays_buttons = [{"text": day, "callback_data": "ignore"} for day in weekdays]
        buttons.append(weekdays_buttons)
        
        # Дни месяца
        first_day = datetime(year, month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        days_in_month = last_day.day
        first_weekday = first_day.weekday()  # 0 = понедельник
        
        # Создаем календарную сетку
        current_date = first_day
        row = []
        
        # Пустые кнопки для начала месяца
        for _ in range(first_weekday):
            row.append({"text": " ", "callback_data": "ignore"})
        
        # Дни месяца
        for day in range(1, days_in_month + 1):
            current_date = datetime(year, month, day)
            today = datetime.now()
            
            # Форматируем дату как в оригинальном коде: ДД.ММ.ГГГГ
            date_str = f"{day:02d}.{month:02d}.{year}"
            
            # Выделяем сегодняшний день
            if current_date.date() == today.date():
                button_text = f"✈️ {day}"
            else:
                button_text = str(day)
            
            # Игнорируем прошедшие даты
            callback_data = f"date_{date_str}" if current_date.date() >= today.date() else "ignore"
            
            row.append({
                "text": button_text,
                "callback_data": callback_data
            })
            
            # Переход на новую строку каждые 7 дней
            if len(row) == 7:
                buttons.append(row)
                row = []
        
        # Добавляем оставшиеся кнопки
        if row:
            buttons.append(row)
        
        # Кнопка "Назад в главное меню"
        buttons.append([{"text": "⬅️ Назад в главное меню", "callback_data": "back_to_start"}])
        
        return self.create_inline_keyboard(buttons)
    
    def create_position_keyboard(self) -> Dict[str, Any]:
        """Создание клавиатуры для выбора должности"""
        buttons = []
        
        # Создаем кнопки должностей (по одной в ряд)
        for position in self.positions:
            buttons.append([{"text": position, "callback_data": f"position_{position}"}])
        
        # Кнопка "Назад к выбору даты"
        buttons.append([{"text": "⬅️ Назад к выбору даты", "callback_data": "back_to_date_selection"}])
        
        return self.create_inline_keyboard(buttons)
    
    def create_direction_keyboard(self, location: str) -> Dict[str, Any]:
        """Создание клавиатуры для выбора направления"""
        directions_list = self.directions.get(location, [])
        buttons = []
        
        # Создаем кнопки направлений (по 2 в ряд)
        for i in range(0, len(directions_list), 2):
            row = []
            for j in range(2):
                if i + j < len(directions_list):
                    direction = directions_list[i + j]
                    row.append({
                        "text": direction,
                        "callback_data": f"direction_{direction}"
                    })
            buttons.append(row)
        
        # Кнопка для ручного ввода направления
        buttons.append([{"text": "✏️ Указать свое направление", "callback_data": "manual_direction_input"}])
        
        # Кнопка "Назад к выбору даты"
        buttons.append([{"text": "⬅️ Назад к выбору даты", "callback_data": "back_to_date_selection"}])
        
        return self.create_inline_keyboard(buttons)
    
    def create_fio_keyboard(self, has_last_data: bool = False, last_fio: str = "", last_tab_num: str = "") -> Dict[str, Any]:
        """Создание клавиатуры для ввода ФИО"""
        buttons = []
        
        if has_last_data and last_fio and last_tab_num:
            # Кнопка подтверждения последних данных
            buttons.append([{"text": "✅ Подтвердить последние данные", "callback_data": "confirm_last_fio_tabnum"}])
        
        # Кнопка "Назад к выбору должности"
        buttons.append([{"text": "⬅️ Назад к выбору должности", "callback_data": "back_to_date_selection"}])
        
        return self.create_inline_keyboard(buttons)
    
    def create_confirmation_keyboard(self) -> Dict[str, Any]:
        """Создание клавиатуры для подтверждения заявки"""
        buttons = [
            [
                {"text": "✅ Подтвердить", "callback_data": "confirm_application"},
                {"text": "✏️ Изменить", "callback_data": "back_to_start"}
            ]
        ]
        return self.create_inline_keyboard(buttons)
    
    def process_express_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщения от Express.ms"""
        try:
            message_type = message_data.get('type', '')
            user_id = message_data.get('user_id', '')
            text = message_data.get('text', '').strip()
            
            logger.info(f"Получено сообщение от {user_id}: {text}")
            
            # Обработка команды /start
            if text == '/start':
                return self.handle_start_command(user_id)
            
            # Обработка callback запросов
            if message_type == 'callback_query':
                callback_data = message_data.get('callback_data', '')
                return self.handle_callback_query(user_id, callback_data)
            
            # Обработка обычных сообщений
            if user_id in self.user_sessions:
                return self.handle_text_message(user_id, text)
            
            # Если нет активной сессии
            return {
                "text": "🤖 Используйте команду /start для начала работы с ботом",
                "reply_markup": self.create_start_keyboard()
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return {
                "text": "❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз.",
                "reply_markup": self.create_start_keyboard()
            }
    
    def handle_start_command(self, user_id: str) -> Dict[str, Any]:
        """Обработка команды /start"""
        # Получаем активные периоды
        periods = asyncio.run(self.get_application_periods())
        
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
        
        return {
            "text": welcome_text,
            "reply_markup": self.create_start_keyboard()
        }
    
    def handle_callback_query(self, user_id: str, callback_data: str) -> Dict[str, Any]:
        """Обработка callback запросов от инлайн кнопок"""
        logger.info(f"Callback от пользователя {user_id}: {callback_data}")
        
        # Обработка различных callback'ов
        if callback_data == "back_to_start":
            # Очищаем состояние пользователя
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            return self.handle_start_command(user_id)
        
        elif callback_data.startswith("location_"):
            return self.handle_location_selection(user_id, callback_data)
        
        elif callback_data.startswith("oke_"):
            return self.handle_oke_selection(user_id, callback_data)
        
        elif callback_data.startswith("nav_month_"):
            return self.handle_calendar_navigation(user_id, callback_data)
        
        elif callback_data.startswith("date_"):
            return self.handle_date_selection(user_id, callback_data)
        
        elif callback_data.startswith("position_"):
            return self.handle_position_selection(user_id, callback_data)
        
        elif callback_data.startswith("direction_"):
            return self.handle_direction_selection(user_id, callback_data)
        
        elif callback_data == "manual_direction_input":
            return self.handle_manual_direction_input(user_id)
        
        elif callback_data == "confirm_last_fio_tabnum":
            return self.handle_confirm_last_fio(user_id)
        
        elif callback_data == "confirm_application":
            return self.handle_confirm_application(user_id)
        
        elif callback_data == "back_to_date_selection":
            return self.handle_back_to_date_selection(user_id)
        
        else:
            return {
                "text": "❓ Неизвестная команда",
                "reply_markup": self.create_start_keyboard()
            }
    
    def handle_location_selection(self, user_id: str, callback_data: str) -> Dict[str, Any]:
        """Обработка выбора локации"""
        location = callback_data.replace("location_", "")
        
        # Инициализируем сессию пользователя
        self.user_sessions[user_id] = {
            'step': 'oke',
            'data': {'location': location}
        }
        
        return {
            "text": f"✅ Вы выбрали локацию: **{location}**!\n\n👌 Отлично!\nТеперь выберите ваше **Подразделение** для *{location}*:",
            "reply_markup": self.create_oke_keyboard(location)
        }
    
    def handle_oke_selection(self, user_id: str, callback_data: str) -> Dict[str, Any]:
        """Обработка выбора ОКЭ"""
        oke = callback_data.replace("oke_", "")
        
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        self.user_sessions[user_id]['data']['oke'] = oke
        self.user_sessions[user_id]['step'] = 'calendar'
        
        return {
            "text": f"✅ Вы выбрали ОКЭ: **{oke}**!\n\n🗓️ Выберите **дату** для рейса:",
            "reply_markup": self.create_calendar_keyboard()
        }
    
    def handle_calendar_navigation(self, user_id: str, callback_data: str) -> Dict[str, Any]:
        """Обработка навигации по календарю"""
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        # Парсим параметры навигации
        parts = callback_data.split("_")
        year = int(parts[2])
        month = int(parts[3])
        
        return {
            "text": "🗓️ Выберите **дату** для рейса:",
            "reply_markup": self.create_calendar_keyboard(year, month)
        }
    
    def handle_date_selection(self, user_id: str, callback_data: str) -> Dict[str, Any]:
        """Обработка выбора даты"""
        date_str = callback_data.replace("date_", "")
        
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        self.user_sessions[user_id]['data']['date'] = date_str
        self.user_sessions[user_id]['step'] = 'position'
        
        return {
            "text": f"✅ Выбрана дата: **{date_str}**!\n\n👨‍✈️ Выберите вашу **должность**:",
            "reply_markup": self.create_position_keyboard()
        }
    
    def handle_position_selection(self, user_id: str, callback_data: str) -> Dict[str, Any]:
        """Обработка выбора должности"""
        position = callback_data.replace("position_", "")
        
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        self.user_sessions[user_id]['data']['position'] = position
        self.user_sessions[user_id]['step'] = 'fio'
        
        # Проверяем, есть ли сохраненные данные пользователя
        has_last_data = False  # В реальной реализации здесь должна быть проверка сохраненных данных
        last_fio = ""
        last_tab_num = ""
        
        fio_text = """📝 Отлично!
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
        
        if has_last_data:
            fio_text += f"""
Если ваши данные не изменились, можете просто подтвердить:
```
{last_fio}
{last_tab_num}
```
Или нажмите кнопку ниже:"""
        
        return {
            "text": fio_text,
            "reply_markup": self.create_fio_keyboard(has_last_data, last_fio, last_tab_num)
        }
    
    def handle_direction_selection(self, user_id: str, callback_data: str) -> Dict[str, Any]:
        """Обработка выбора направления"""
        direction = callback_data.replace("direction_", "")
        
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        self.user_sessions[user_id]['data']['direction'] = direction
        self.user_sessions[user_id]['step'] = 'wishes'
        
        return {
            "text": f"✅ Вы выбрали направление: **{direction}**!\n\n📝 Отлично! Теперь укажите ваши пожелания. Если пожелания отсутствуют, то поставьте прочерк:"
        }
    
    def handle_manual_direction_input(self, user_id: str) -> Dict[str, Any]:
        """Обработка запроса на ручной ввод направления"""
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        self.user_sessions[user_id]['step'] = 'manual_direction'
        
        return {
            "text": "📝 Пожалуйста, введите **название направления** текстом:"
        }
    
    def handle_confirm_last_fio(self, user_id: str) -> Dict[str, Any]:
        """Обработка подтверждения последних ФИО"""
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        # В реальной реализации здесь должны быть получены сохраненные данные
        # Пока используем заглушку
        fio = "Соколянский А.В."
        tab_num = "119356"
        
        self.user_sessions[user_id]['data']['fio'] = fio
        self.user_sessions[user_id]['data']['tab_num'] = tab_num
        self.user_sessions[user_id]['step'] = 'direction'
        
        location = self.user_sessions[user_id]['data']['location']
        
        return {
            "text": f"✅ Вы подтвердили последние ФИО и Табельный номер!\n\n🌍 Выберите **направление** вашего рейса или введите его вручную:",
            "reply_markup": self.create_direction_keyboard(location)
        }
    
    def handle_confirm_application(self, user_id: str) -> Dict[str, Any]:
        """Обработка подтверждения заявки"""
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        session = self.user_sessions[user_id]
        
        # Отправляем заявку
        application_data = {
            **session['data'],
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        result = asyncio.run(self.submit_application(application_data))
        
        if result.get('success'):
            success_text = """🎉 Поздравляем! Ваши данные успешно отправлены и сохранены.

Напоминаем, что заказ рейса — это возможность, а не гарантия его выполнения. Итоговое решение остается за ЦП при обеспечении плана полетов.

Чтобы вернуться в главное меню и начать заново, нажмите /start."""
            
            # Очищаем сессию
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            
            self.stats['total_applications'] += 1
            
            return {
                "text": success_text,
                "reply_markup": self.create_start_keyboard()
            }
        else:
            error_text = f"""❌ **Ошибка при подаче заявки**

Причина: {result.get('error', 'Неизвестная ошибка')}

Попробуйте еще раз с помощью команды /start."""
            
            return {
                "text": error_text,
                "reply_markup": self.create_start_keyboard()
            }
    
    def handle_back_to_date_selection(self, user_id: str) -> Dict[str, Any]:
        """Обработка возврата к выбору даты"""
        if user_id not in self.user_sessions:
            return self.handle_start_command(user_id)
        
        # Очищаем данные после выбора даты
        session = self.user_sessions[user_id]
        session['data'] = {
            'location': session['data'].get('location'),
            'oke': session['data'].get('oke')
        }
        session['step'] = 'calendar'
        
        return {
            "text": "🗓️ Выберите **дату** для рейса:",
            "reply_markup": self.create_calendar_keyboard()
        }
    
    def handle_text_message(self, user_id: str, text: str) -> Dict[str, Any]:
        """Обработка обычных текстовых сообщений"""
        if user_id not in self.user_sessions:
            return {
                "text": "🤖 Используйте кнопки для работы с ботом или команды:\n• `/start` - Начать работу\n• `/help` - Справка",
                "reply_markup": self.create_start_keyboard()
            }
        
        session = self.user_sessions[user_id]
        step = session['step']
        
        if step == 'fio':
            # Обработка ввода ФИО и табельного номера
            lines = text.split('\n')
            if len(lines) >= 2:
                fio = lines[0].strip()
                tab_num = lines[1].strip()
                
                session['data']['fio'] = fio
                session['data']['tab_num'] = tab_num
                session['step'] = 'direction'
                
                location = session['data']['location']
                return {
                    "text": f"✅ Вы подтвердили последние ФИО и Табельный номер!\n\n🌍 Выберите **направление** вашего рейса или введите его вручную:",
                    "reply_markup": self.create_direction_keyboard(location)
                }
            else:
                return {
                    "text": "⚠️ **Ошибка формата!** Пожалуйста, убедитесь, что вы отправили **ФИО и Табельный номер** в отдельных строках.\n\nПример корректного формата:\n```\nСоколянский А.В.\n119356\n```"
                }
        
        elif step == 'manual_direction':
            # Обработка ручного ввода направления
            session['data']['direction'] = text
            session['step'] = 'wishes'
            
            return {
                "text": f"✅ Вы указали направление: **{text}**!\n\n📝 Отлично! Теперь укажите ваши пожелания. Если пожелания отсутствуют, то поставьте прочерк:"
            }
        
        elif step == 'wishes':
            # Обработка ввода пожеланий
            session['data']['wishes'] = text
            session['step'] = 'confirmation'
            
            # Показываем сводку для подтверждения
            data = session['data']
            summary = f"""✨ **Пожалуйста, проверьте вашу заявку перед отправкой:**

Локация: **{data.get('location', 'Не указана')}**
ОКЭ: **{data.get('oke', 'Не указано')}**
Дата: **{data.get('date', 'Не указана')}**
Должность: **{data.get('position', 'Не указана')}**
ФИО: **{data.get('fio', 'Не указано')}**
Табельный номер: **{data.get('tab_num', 'Не указан')}**
Направление: **{data.get('direction', 'Не указано')}**
Пожелания: **{data.get('wishes', 'Не указаны')}**"""
            
            return {
                "text": summary,
                "reply_markup": self.create_confirmation_keyboard()
            }
        
        else:
            return {
                "text": "🤖 Используйте кнопки для работы с ботом или команды:\n• `/start` - Начать работу\n• `/help` - Справка",
                "reply_markup": self.create_start_keyboard()
            }

# Создаем экземпляр бота
bot = CloudPubFlightBookingBot()

# Flask маршруты
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "bot_id": BOT_CONFIG['bot_id'],
        "cloudpub_url": BOT_CONFIG['cloudpub_url'],
        "uptime": str(datetime.now() - bot.stats['start_time']),
        "active_sessions": len(bot.user_sessions),
        "total_applications": bot.stats['total_applications']
    })

@app.route('/manifest', methods=['GET'])
def manifest():
    """Manifest для Express.ms"""
    return jsonify({
        "name": BOT_CONFIG['bot_name'],
        "description": BOT_CONFIG['bot_description'],
        "version": "1.0.0",
        "bot_id": BOT_CONFIG['bot_id'],
        "webhook_url": BOT_CONFIG['webhook_url'],
        "capabilities": [
            "message_handling",
            "inline_keyboards",
            "callback_queries",
            "application_submission"
        ]
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint для Express.ms"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        logger.info(f"Получен webhook: {data}")
        
        # Обрабатываем сообщение
        response = bot.process_express_message(data)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/admin', methods=['GET'])
def admin_panel():
    """Админ панель"""
    admin_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Express Bot Admin Panel</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #333; margin-bottom: 30px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
            .stat-label { color: #666; margin-top: 5px; }
            .info { background: #e7f3ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .info h3 { margin-top: 0; color: #0066cc; }
            .refresh-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .refresh-btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Express Bot Admin Panel</h1>
                <p>Система подачи заявок на командировочные рейсы</p>
            </div>
            
            <div class="info">
                <h3>📋 Информация о боте</h3>
                <p><strong>Bot ID:</strong> """ + BOT_CONFIG['bot_id'] + """</p>
                <p><strong>CloudPub URL:</strong> """ + BOT_CONFIG['cloudpub_url'] + """</p>
                <p><strong>Webhook URL:</strong> """ + BOT_CONFIG['webhook_url'] + """</p>
                <p><strong>Статус:</strong> <span style="color: green;">🟢 Онлайн</span></p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="total-applications">""" + str(bot.stats['total_applications']) + """</div>
                    <div class="stat-label">Всего заявок</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="active-sessions">""" + str(len(bot.user_sessions)) + """</div>
                    <div class="stat-label">Активных сессий</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="uptime">""" + str(datetime.now() - bot.stats['start_time']).split('.')[0] + """</div>
                    <div class="stat-label">Время работы</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <button class="refresh-btn" onclick="location.reload()">🔄 Обновить</button>
            </div>
        </div>
        
        <script>
            // Автообновление каждые 30 секунд
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    return admin_html

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API для получения статистики"""
    return jsonify({
        "total_applications": bot.stats['total_applications'],
        "active_sessions": len(bot.user_sessions),
        "uptime": str(datetime.now() - bot.stats['start_time']),
        "start_time": bot.stats['start_time'].isoformat(),
        "bot_id": BOT_CONFIG['bot_id'],
        "cloudpub_url": BOT_CONFIG['cloudpub_url']
    })

if __name__ == '__main__':
    logger.info("🚀 Запуск Express Bot для CloudPub...")
    logger.info(f"📱 Bot ID: {BOT_CONFIG['bot_id']}")
    logger.info(f"🌐 CloudPub URL: {BOT_CONFIG['cloudpub_url']}")
    logger.info(f"🔗 Webhook URL: {BOT_CONFIG['webhook_url']}")
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=5011, debug=False)
