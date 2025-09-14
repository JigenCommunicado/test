#!/usr/bin/env python3
"""
Express Bot Final - Финальная версия на основе кода из скриншотов
Система подачи заявок на рейсы с полной функциональностью
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, IncomingMessage, StatusRecipient, OutgoingMessage, KeyboardMarkup, Button, ButtonRow

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
        'api_base_url': config_manager.get('bot_settings.api_base_url', 'http://localhost:5002'),
        'bot_name': config_manager.get('bot_settings.bot_name', 'Flight Booking Bot'),
        'bot_description': config_manager.get('bot_settings.bot_description', 'Бот для подачи заявок на командировочные рейсы')
    }
except ImportError:
    # Fallback к старой конфигурации если config_manager недоступен
    BOT_CONFIG = {
        'bot_id': os.environ.get('EXPRESS_BOT_ID', '00c46d64-1127-5a96-812d-3d8b27c58b99'),
        'secret_key': os.environ.get('EXPRESS_SECRET_KEY', 'a75b4cd97d9e88e543f077178b2d5a4f'),
        'api_base_url': os.environ.get('FLASK_API_URL', 'http://localhost:5002'),
        'bot_name': 'Flight Booking Bot',
        'bot_description': 'Бот для подачи заявок на командировочные рейсы'
    }

# Создаем коллектор обработчиков
collector = HandlerCollector()

# Создаем аккаунт бота для Express.ms
# ВАЖНО: Express.ms использует другой API, не pybotx
# Нужно использовать REST API Express.ms
bot_account = BotAccountWithSecret(
    id=BOT_CONFIG['bot_id'],
    secret_key=BOT_CONFIG['secret_key'],
    host="https://api.express.ms",  # Правильный API endpoint
    cts_url="https://api.express.ms"  # Правильный CTS endpoint
)

# Создаем экземпляр бота
bot = Bot(collectors=[collector], bot_accounts=[bot_account])

class FinalFlightBookingBot:
    """Финальный класс бота на основе кода из скриншотов"""
    
    def __init__(self):
        self.api_url = BOT_CONFIG['api_base_url']
        self.user_sessions = {}
        
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
            import aiohttp
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
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/api/application", json=user_data) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"Ошибка отправки заявки: {e}")
        return {"success": False, "error": "Ошибка отправки заявки"}
    
    def create_start_keyboard(self) -> KeyboardMarkup:
        """Создание стартового меню с выбором локации"""
        buttons = []
        
        # Первый ряд: Москва и СПб
        row1 = ButtonRow()
        row1.add_button(Button(
            text="🏙️ Москва",
            callback_data="location_МСК"
        ))
        row1.add_button(Button(
            text="🌉 Санкт-Петербург",
            callback_data="location_СПБ"
        ))
        buttons.append(row1)
        
        # Второй ряд: Красноярск и Сочи
        row2 = ButtonRow()
        row2.add_button(Button(
            text="🏞️ Красноярск",
            callback_data="location_Красноярск"
        ))
        row2.add_button(Button(
            text="🏖️ Сочи",
            callback_data="location_Сочи"
        ))
        buttons.append(row2)
        
        return KeyboardMarkup(buttons)
    
    def create_oke_keyboard(self, location: str) -> KeyboardMarkup:
        """Создание клавиатуры для выбора ОКЭ"""
        buttons = []
        oke_list = self.oke_by_location.get(location, ['ОЛСиТ'])
        
        # Создаем кнопки ОКЭ
        for i in range(0, len(oke_list), 2):
            row = ButtonRow()
            for j in range(2):
                if i + j < len(oke_list):
                    oke = oke_list[i + j]
                    row.add_button(Button(
                        text=oke,
                        callback_data=f"oke_{oke}"
                    ))
            buttons.append(row)
        
        # Кнопка "Назад в главное меню"
        back_row = ButtonRow()
        back_row.add_button(Button(
            text="⬅️ Назад в главное меню",
            callback_data="back_to_start"
        ))
        buttons.append(back_row)
        
        return KeyboardMarkup(buttons)
    
    def create_calendar_keyboard(self, year: int = None, month: int = None) -> KeyboardMarkup:
        """Создание клавиатуры календаря (как в оригинальном коде)"""
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
        nav_row = ButtonRow()
        nav_row.add_button(Button(
            text="⬅️",
            callback_data=f"nav_month_{year}_{month-1 if month > 1 else 12}_{year-1 if month == 1 else year}"
        ))
        nav_row.add_button(Button(
            text=f"{month_names[month-1]} {year}",
            callback_data="ignore"
        ))
        nav_row.add_button(Button(
            text="➡️",
            callback_data=f"nav_month_{year}_{month+1 if month < 12 else 1}_{year+1 if month == 12 else year}"
        ))
        buttons.append(nav_row)
        
        # Дни недели
        weekdays_row = ButtonRow()
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            weekdays_row.add_button(Button(
                text=day,
                callback_data="ignore"
            ))
        buttons.append(weekdays_row)
        
        # Дни месяца
        first_day = datetime(year, month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        days_in_month = last_day.day
        first_weekday = first_day.weekday()  # 0 = понедельник
        
        # Создаем календарную сетку
        current_date = first_day
        row = ButtonRow()
        
        # Пустые кнопки для начала месяца
        for _ in range(first_weekday):
            row.add_button(Button(text=" ", callback_data="ignore"))
        
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
            
            row.add_button(Button(
                text=button_text,
                callback_data=callback_data
            ))
            
            # Переход на новую строку каждые 7 дней
            if len(row.buttons) == 7:
                buttons.append(row)
                row = ButtonRow()
        
        # Добавляем оставшиеся кнопки
        if row.buttons:
            buttons.append(row)
        
        # Кнопка "Назад в главное меню"
        back_row = ButtonRow()
        back_row.add_button(Button(
            text="⬅️ Назад в главное меню",
            callback_data="back_to_start"
        ))
        buttons.append(back_row)
        
        return KeyboardMarkup(buttons)
    
    def create_position_keyboard(self) -> KeyboardMarkup:
        """Создание клавиатуры для выбора должности"""
        buttons = []
        
        # Создаем кнопки должностей (по одной в ряд, как в оригинале)
        for position in self.positions:
            row = ButtonRow()
            row.add_button(Button(
                text=position,
                callback_data=f"position_{position}"
            ))
            buttons.append(row)
        
        # Кнопка "Назад к выбору даты"
        back_row = ButtonRow()
        back_row.add_button(Button(
            text="⬅️ Назад к выбору даты",
            callback_data="back_to_date_selection"
        ))
        buttons.append(back_row)
        
        return KeyboardMarkup(buttons)
    
    def create_direction_keyboard(self, location: str) -> KeyboardMarkup:
        """Создание клавиатуры для выбора направления"""
        buttons = []
        directions_list = self.directions.get(location, [])
        
        # Создаем кнопки направлений (по 2 в ряд)
        for i in range(0, len(directions_list), 2):
            row = ButtonRow()
            for j in range(2):
                if i + j < len(directions_list):
                    direction = directions_list[i + j]
                    row.add_button(Button(
                        text=direction,
                        callback_data=f"direction_{direction}"
                    ))
            buttons.append(row)
        
        # Кнопка для ручного ввода направления
        manual_row = ButtonRow()
        manual_row.add_button(Button(
            text="✏️ Указать свое направление",
            callback_data="manual_direction_input"
        ))
        buttons.append(manual_row)
        
        # Кнопка "Назад к выбору даты"
        back_row = ButtonRow()
        back_row.add_button(Button(
            text="⬅️ Назад к выбору даты",
            callback_data="back_to_date_selection"
        ))
        buttons.append(back_row)
        
        return KeyboardMarkup(buttons)
    
    def create_fio_keyboard(self, has_last_data: bool = False, last_fio: str = "", last_tab_num: str = "") -> KeyboardMarkup:
        """Создание клавиатуры для ввода ФИО"""
        buttons = []
        
        if has_last_data and last_fio and last_tab_num:
            # Кнопка подтверждения последних данных
            confirm_row = ButtonRow()
            confirm_row.add_button(Button(
                text="✅ Подтвердить последние данные",
                callback_data="confirm_last_fio_tabnum"
            ))
            buttons.append(confirm_row)
        
        # Кнопка "Назад к выбору должности"
        back_row = ButtonRow()
        back_row.add_button(Button(
            text="⬅️ Назад к выбору должности",
            callback_data="back_to_date_selection"
        ))
        buttons.append(back_row)
        
        return KeyboardMarkup(buttons)
    
    def create_confirmation_keyboard(self) -> KeyboardMarkup:
        """Создание клавиатуры для подтверждения заявки"""
        buttons = []
        
        # Кнопки подтверждения и изменения
        action_row = ButtonRow()
        action_row.add_button(Button(
            text="✅ Подтвердить",
            callback_data="confirm_application"
        ))
        action_row.add_button(Button(
            text="✏️ Изменить",
            callback_data="back_to_start"
        ))
        buttons.append(action_row)
        
        return KeyboardMarkup(buttons)

# Создаем экземпляр финального бота
final_bot = FinalFlightBookingBot()

@collector.command("/start", description="Начать работу с ботом")
async def start_handler(message: IncomingMessage, bot: Bot) -> None:
    """Обработчик команды /start с приветствием и правилами"""
    user_id = str(message.user.huid)
    
    # Получаем активные периоды
    periods = await final_bot.get_application_periods()
    
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
    
    keyboard = final_bot.create_start_keyboard()
    
    await bot.send(
        message.reply(welcome_text, keyboard=keyboard)
    )

async def handle_callback_query(message: IncomingMessage, bot: Bot) -> None:
    """Обработчик callback запросов от инлайн кнопок"""
    user_id = str(message.user.huid)
    
    # Проверяем, есть ли callback_query в сообщении
    if not hasattr(message, 'callback_query') or not message.callback_query:
        return
    
    callback_data = message.callback_query.data
    logger.info(f"Callback от пользователя {user_id}: {callback_data}")
    
    # Обработка различных callback'ов
    if callback_data == "back_to_start":
        await start_handler(message, bot)
        # Очищаем состояние пользователя
        if user_id in final_bot.user_sessions:
            del final_bot.user_sessions[user_id]
    
    elif callback_data.startswith("location_"):
        await handle_location_selection(message, bot, callback_data)
    
    elif callback_data.startswith("oke_"):
        await handle_oke_selection(message, bot, callback_data)
    
    elif callback_data.startswith("nav_month_"):
        await handle_calendar_navigation(message, bot, callback_data)
    
    elif callback_data.startswith("date_"):
        await handle_date_selection(message, bot, callback_data)
    
    elif callback_data.startswith("position_"):
        await handle_position_selection(message, bot, callback_data)
    
    elif callback_data.startswith("direction_"):
        await handle_direction_selection(message, bot, callback_data)
    
    elif callback_data == "manual_direction_input":
        await handle_manual_direction_input(message, bot)
    
    elif callback_data == "confirm_last_fio_tabnum":
        await handle_confirm_last_fio(message, bot)
    
    elif callback_data == "confirm_application":
        await handle_confirm_application(message, bot)
    
    elif callback_data == "back_to_date_selection":
        await handle_back_to_date_selection(message, bot)
    
    else:
        await bot.send(message.reply("❓ Неизвестная команда"))

async def handle_location_selection(message: IncomingMessage, bot: Bot, callback_data: str) -> None:
    """Обработка выбора локации"""
    user_id = str(message.user.huid)
    location = callback_data.replace("location_", "")
    
    # Инициализируем сессию пользователя
    final_bot.user_sessions[user_id] = {
        'step': 'oke',
        'data': {'location': location}
    }
    
    keyboard = final_bot.create_oke_keyboard(location)
    await bot.send(
        message.reply(
            f"✅ Вы выбрали локацию: **{location}**!\n\n"
            f"👌 Отлично!\n"
            f"Теперь выберите ваше **Подразделение** для *{location}*:"
        ),
        keyboard=keyboard
    )

async def handle_oke_selection(message: IncomingMessage, bot: Bot, callback_data: str) -> None:
    """Обработка выбора ОКЭ"""
    user_id = str(message.user.huid)
    oke = callback_data.replace("oke_", "")
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    final_bot.user_sessions[user_id]['data']['oke'] = oke
    final_bot.user_sessions[user_id]['step'] = 'calendar'
    
    keyboard = final_bot.create_calendar_keyboard()
    await bot.send(
        message.reply(
            f"✅ Вы выбрали ОКЭ: **{oke}**!\n\n"
            f"🗓️ Выберите **дату** для рейса:"
        ),
        keyboard=keyboard
    )

async def handle_calendar_navigation(message: IncomingMessage, bot: Bot, callback_data: str) -> None:
    """Обработка навигации по календарю"""
    user_id = str(message.user.huid)
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    # Парсим параметры навигации
    parts = callback_data.split("_")
    year = int(parts[2])
    month = int(parts[3])
    
    keyboard = final_bot.create_calendar_keyboard(year, month)
    await bot.send(
        message.reply(
            f"🗓️ Выберите **дату** для рейса:"
        ),
        keyboard=keyboard
    )

async def handle_date_selection(message: IncomingMessage, bot: Bot, callback_data: str) -> None:
    """Обработка выбора даты"""
    user_id = str(message.user.huid)
    date_str = callback_data.replace("date_", "")
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    final_bot.user_sessions[user_id]['data']['date'] = date_str
    final_bot.user_sessions[user_id]['step'] = 'position'
    
    keyboard = final_bot.create_position_keyboard()
    await bot.send(
        message.reply(
            f"✅ Выбрана дата: **{date_str}**!\n\n"
            f"👨‍✈️ Выберите вашу **должность**:"
        ),
        keyboard=keyboard
    )

async def handle_position_selection(message: IncomingMessage, bot: Bot, callback_data: str) -> None:
    """Обработка выбора должности"""
    user_id = str(message.user.huid)
    position = callback_data.replace("position_", "")
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    final_bot.user_sessions[user_id]['data']['position'] = position
    final_bot.user_sessions[user_id]['step'] = 'fio'
    
    # Проверяем, есть ли сохраненные данные пользователя
    has_last_data = False  # В реальной реализации здесь должна быть проверка сохраненных данных
    last_fio = ""
    last_tab_num = ""
    
    keyboard = final_bot.create_fio_keyboard(has_last_data, last_fio, last_tab_num)
    
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
    
    await bot.send(
        message.reply(fio_text),
        keyboard=keyboard
    )

async def handle_direction_selection(message: IncomingMessage, bot: Bot, callback_data: str) -> None:
    """Обработка выбора направления"""
    user_id = str(message.user.huid)
    direction = callback_data.replace("direction_", "")
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    final_bot.user_sessions[user_id]['data']['direction'] = direction
    final_bot.user_sessions[user_id]['step'] = 'wishes'
    
    await bot.send(
        message.reply(
            f"✅ Вы выбрали направление: **{direction}**!\n\n"
            f"📝 Отлично! Теперь укажите ваши пожелания. Если пожелания отсутствуют, то поставьте прочерк:"
        )
    )

async def handle_manual_direction_input(message: IncomingMessage, bot: Bot) -> None:
    """Обработка запроса на ручной ввод направления"""
    user_id = str(message.user.huid)
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    final_bot.user_sessions[user_id]['step'] = 'manual_direction'
    
    await bot.send(
        message.reply(
            "📝 Пожалуйста, введите **название направления** текстом:"
        )
    )

async def handle_confirm_last_fio(message: IncomingMessage, bot: Bot) -> None:
    """Обработка подтверждения последних ФИО"""
    user_id = str(message.user.huid)
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    # В реальной реализации здесь должны быть получены сохраненные данные
    # Пока используем заглушку
    fio = "Соколянский А.В."
    tab_num = "119356"
    
    final_bot.user_sessions[user_id]['data']['fio'] = fio
    final_bot.user_sessions[user_id]['data']['tab_num'] = tab_num
    final_bot.user_sessions[user_id]['step'] = 'direction'
    
    location = final_bot.user_sessions[user_id]['data']['location']
    keyboard = final_bot.create_direction_keyboard(location)
    
    await bot.send(
        message.reply(
            f"✅ Вы подтвердили последние ФИО и Табельный номер!\n\n"
            f"🌍 Выберите **направление** вашего рейса или введите его вручную:"
        ),
        keyboard=keyboard
    )

async def handle_confirm_application(message: IncomingMessage, bot: Bot) -> None:
    """Обработка подтверждения заявки"""
    user_id = str(message.user.huid)
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    session = final_bot.user_sessions[user_id]
    
    # Показываем индикатор загрузки
    await bot.send(message.reply("⌛ Обрабатываю ваш запрос... Пожалуйста, подождите немного."))
    
    # Отправляем заявку
    application_data = {
        **session['data'],
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    }
    
    result = await final_bot.submit_application(application_data)
    
    if result.get('success'):
        success_text = """🎉 Поздравляем! Ваши данные успешно отправлены и сохранены.

Напоминаем, что заказ рейса — это возможность, а не гарантия его выполнения. Итоговое решение остается за ЦП при обеспечении плана полетов.

Чтобы вернуться в главное меню и начать заново, нажмите /start."""
        
        keyboard = final_bot.create_start_keyboard()
        await bot.send(message.reply(success_text, keyboard=keyboard))
    else:
        error_text = f"""❌ **Ошибка при подаче заявки**

Причина: {result.get('error', 'Неизвестная ошибка')}

Попробуйте еще раз с помощью команды /start."""
        
        keyboard = final_bot.create_start_keyboard()
        await bot.send(message.reply(error_text, keyboard=keyboard))
    
    # Очищаем сессию
    if user_id in final_bot.user_sessions:
        del final_bot.user_sessions[user_id]

async def handle_back_to_date_selection(message: IncomingMessage, bot: Bot) -> None:
    """Обработка возврата к выбору даты"""
    user_id = str(message.user.huid)
    
    if user_id not in final_bot.user_sessions:
        await start_handler(message, bot)
        return
    
    # Очищаем данные после выбора даты
    session = final_bot.user_sessions[user_id]
    session['data'] = {
        'location': session['data'].get('location'),
        'oke': session['data'].get('oke')
    }
    session['step'] = 'calendar'
    
    keyboard = final_bot.create_calendar_keyboard()
    await bot.send(
        message.reply(
            f"🗓️ Выберите **дату** для рейса:"
        ),
        keyboard=keyboard
    )

@collector.default_message_handler
async def message_handler(message: IncomingMessage, bot: Bot) -> None:
    """Обработчик обычных сообщений для продолжения диалога"""
    user_id = str(message.user.huid)
    
    # Сначала проверяем, есть ли callback_query
    await handle_callback_query(message, bot)
    
    # Если это не callback, обрабатываем как обычное сообщение
    if not hasattr(message, 'callback_query') or not message.callback_query:
        text = message.body.strip()
        
        # Проверяем, есть ли активная сессия
        if user_id not in final_bot.user_sessions:
            keyboard = final_bot.create_start_keyboard()
            await bot.send(
                message.reply(
                    "🤖 Используйте кнопки для работы с ботом или команды:\n"
                    "• `/start` - Начать работу\n"
                    "• `/help` - Справка"
                ),
                keyboard=keyboard
            )
            return
        
        session = final_bot.user_sessions[user_id]
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
                keyboard = final_bot.create_direction_keyboard(location)
                await bot.send(
                    message.reply(
                        f"✅ Вы подтвердили последние ФИО и Табельный номер!\n\n"
                        f"🌍 Выберите **направление** вашего рейса или введите его вручную:"
                    ),
                    keyboard=keyboard
                )
            else:
                await bot.send(
                    message.reply(
                        "⚠️ **Ошибка формата!** Пожалуйста, убедитесь, что вы отправили **ФИО и Табельный номер** в отдельных строках.\n\n"
                        "Пример корректного формата:\n"
                        "```\n"
                        "Соколянский А.В.\n"
                        "119356\n"
                        "```"
                    )
                )
        
        elif step == 'manual_direction':
            # Обработка ручного ввода направления
            session['data']['direction'] = text
            session['step'] = 'wishes'
            
            await bot.send(
                message.reply(
                    f"✅ Вы указали направление: **{text}**!\n\n"
                    f"📝 Отлично! Теперь укажите ваши пожелания. Если пожелания отсутствуют, то поставьте прочерк:"
                )
            )
        
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
            
            keyboard = final_bot.create_confirmation_keyboard()
            await bot.send(message.reply(summary, keyboard=keyboard))

async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск Final Express Flight Booking Bot...")
    logger.info(f"📱 Bot ID: {BOT_CONFIG['bot_id']}")
    logger.info(f"🔗 API URL: {BOT_CONFIG['api_base_url']}")
    
    # Запускаем бота
    await bot.startup()

if __name__ == "__main__":
    asyncio.run(main())
