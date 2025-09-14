"""
Telegram бот для системы подачи заявок на корпоративные рейсы
Поддерживает веб-приложения (Mini Apps) и обычные команды
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """Сессия пользователя"""
    user_id: int
    username: str
    first_name: str
    last_name: str
    language_code: str
    state: str = "main_menu"
    application_data: Dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.application_data is None:
            self.application_data = {}

class FlightBookingBot:
    """Основной класс Telegram бота"""
    
    def __init__(self, token: str, api_base_url: str = "http://localhost:5002"):
        self.token = token
        self.api_base_url = api_base_url
        self.sessions: Dict[int, UserSession] = {}
        self.application = None
        
        # URL для Mini App
        self.mini_app_url = "http://localhost:8080/mobile_booking_ui.html"
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        
        # Создаем или обновляем сессию пользователя
        self.sessions[user.id] = UserSession(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            language_code=user.language_code or "ru"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✈️ Подать заявку", web_app=WebAppInfo(url=self.mini_app_url)),
                InlineKeyboardButton("📋 Мои заявки", callback_data="my_applications")
            ],
            [
                InlineKeyboardButton("📅 Периоды подачи", callback_data="periods"),
                InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="statistics")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎯 **Добро пожаловать в систему подачи заявок на корпоративные рейсы!**

Привет, {user.first_name}! 👋

Я помогу вам:
• ✈️ Подать заявку на корпоративный рейс
• 📋 Просмотреть статус ваших заявок
• 📅 Узнать периоды подачи заявок
• 📊 Получить статистику

Выберите действие:
"""
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
📖 **Помощь по использованию бота**

**Основные команды:**
• /start - Главное меню
• /help - Эта справка
• /status - Статус системы
• /my_applications - Мои заявки

**Как подать заявку:**
1. Нажмите "✈️ Подать заявку"
2. Заполните форму в открывшемся веб-приложении
3. Проверьте данные и отправьте

**Веб-интерфейс:**
• 🖥️ ПК версия: /pc_version
• 📱 Мобильная версия: /mobile_version
• 🎛️ Админ панель: /admin (для администраторов)

**Поддержка:**
При возникновении проблем обратитесь к администратору системы.
"""
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        status_text = f"""
🟢 **Система работает нормально**

📊 **Статус:**
• Приложение: {data.get('app_name', 'N/A')}
• Версия: {data.get('version', 'N/A')}
• Активных пользователей: {data.get('active_users', 'N/A')}
• Время: {data.get('timestamp', 'N/A')}

✅ Все сервисы доступны
"""
                    else:
                        status_text = "🔴 **Система недоступна**\n\nПопробуйте позже или обратитесь к администратору."
        except Exception as e:
            status_text = f"❌ **Ошибка подключения**\n\n`{str(e)}`"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def pc_version_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /pc_version"""
        pc_text = """
🖥️ **ПК версия системы**

Для работы с полной версией системы на компьютере:

🔗 **Ссылки:**
• [Главная навигация](http://localhost:8080/index.html)
• [Форма заявки](http://localhost:8080/flight_booking_ui.html)
• [Админ панель](http://localhost:8080/admin_panel.html)

⚠️ **Внимание:** Ссылки работают только при запущенных серверах
"""
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            pc_text,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    async def mobile_version_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /mobile_version"""
        keyboard = [
            [InlineKeyboardButton("📱 Открыть мобильную версию", web_app=WebAppInfo(url=self.mini_app_url))],
            [InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        mobile_text = """
📱 **Мобильная версия**

Адаптированная версия для смартфонов и планшетов.

Нажмите кнопку ниже для открытия:
"""
        
        await update.message.reply_text(
            mobile_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /admin"""
        # TODO: Добавить проверку прав администратора
        admin_text = """
🎛️ **Панель администратора**

Для администраторов системы:

🔗 **Админ панель:** [Открыть](http://localhost:8080/admin_panel.html)

**Функции:**
• Управление пользователями
• Настройка уведомлений
• Управление периодами подачи заявок
• Просмотр статистики
"""
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            admin_text,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на inline кнопки"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "main_menu":
            await self.show_main_menu(query)
        elif callback_data == "my_applications":
            await self.show_my_applications(query)
        elif callback_data == "periods":
            await self.show_periods(query)
        elif callback_data == "help":
            await self.show_help(query)
        elif callback_data == "statistics":
            await self.show_statistics(query)
    
    async def show_main_menu(self, query):
        """Показать главное меню"""
        keyboard = [
            [
                InlineKeyboardButton("✈️ Подать заявку", web_app=WebAppInfo(url=self.mini_app_url)),
                InlineKeyboardButton("📋 Мои заявки", callback_data="my_applications")
            ],
            [
                InlineKeyboardButton("📅 Периоды подачи", callback_data="periods"),
                InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="statistics")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🎯 **Система подачи заявок на корпоративные рейсы**

Выберите действие:
"""
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_my_applications(self, query):
        """Показать заявки пользователя"""
        try:
            # Получаем заявки пользователя через API
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/statistics") as response:
                    if response.status == 200:
                        data = await response.json()
                        text = f"""
📋 **Мои заявки**

📊 **Общая статистика по системе:**
"""
                        if 'statistics' in data:
                            for oke, count in data['statistics'].items():
                                text += f"• {oke}: {count} заявок\n"
                        else:
                            text += "Данные недоступны"
                    else:
                        text = "❌ Не удалось получить данные о заявках"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_periods(self, query):
        """Показать периоды подачи заявок"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/application-periods") as response:
                    if response.status == 200:
                        data = await response.json()
                        text = "📅 **Периоды подачи заявок**\n\n"
                        
                        if data.get('periods'):
                            for period in data['periods']:
                                status = "🟢 Активен" if period.get('is_active') else "🔴 Неактивен"
                                text += f"**{period.get('name', 'Без названия')}**\n"
                                text += f"📅 {period.get('start_date')} - {period.get('end_date')}\n"
                                text += f"{status}\n\n"
                        else:
                            text += "Периоды не настроены"
                    else:
                        text = "❌ Не удалось получить данные о периодах"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_help(self, query):
        """Показать справку"""
        help_text = """
📖 **Справка**

**Как подать заявку:**
1. Нажмите "✈️ Подать заявку"
2. Заполните форму в веб-приложении
3. Проверьте данные и отправьте

**Команды бота:**
• /start - Главное меню
• /help - Справка
• /status - Статус системы
• /pc_version - ПК версия
• /mobile_version - Мобильная версия
• /admin - Админ панель

**Поддержка:**
При проблемах обратитесь к администратору.
"""
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_statistics(self, query):
        """Показать статистику"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/statistics") as response:
                    if response.status == 200:
                        data = await response.json()
                        text = "📊 **Статистика системы**\n\n"
                        
                        if 'statistics' in data:
                            total = sum(data['statistics'].values())
                            text += f"📈 **Общее количество заявок:** {total}\n\n"
                            text += "**По ОКЭ:**\n"
                            for oke, count in data['statistics'].items():
                                percentage = (count / total * 100) if total > 0 else 0
                                text += f"• {oke}: {count} ({percentage:.1f}%)\n"
                        else:
                            text += "Данные недоступны"
                    else:
                        text = "❌ Не удалось получить статистику"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        await update.message.reply_text(
            "Используйте команды или кнопки для взаимодействия с ботом.\n\nВведите /help для получения справки."
        )
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("pc_version", self.pc_version_command))
        self.application.add_handler(CommandHandler("mobile_version", self.mobile_version_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def run(self):
        """Запуск бота"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        logger.info("🤖 Telegram бот запускается...")
        await self.application.run_polling()

def main():
    """Главная функция"""
    # Получаем токен из переменных окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Ошибка: Не установлен TELEGRAM_BOT_TOKEN")
        print("Создайте бота через @BotFather и установите переменную окружения:")
        print("export TELEGRAM_BOT_TOKEN='ваш_токен_бота'")
        return
    
    # Создаем и запускаем бота
    bot = FlightBookingBot(token)
    
    try:
        # Проверяем наличие активного event loop
        try:
            loop = asyncio.get_running_loop()
            logger.info("Обнаружен активный event loop, используем его")
            # Если есть активный loop, создаем задачу
            asyncio.create_task(bot.run())
        except RuntimeError:
            # Если нет активного loop, создаем новый
            asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
