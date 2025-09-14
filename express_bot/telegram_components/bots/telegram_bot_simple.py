"""
Простой синхронный Telegram бот для системы подачи заявок
Более стабильная версия без async проблем
"""

import os
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FlightBookingBotSimple:
    """Простой Telegram бот для подачи заявок"""
    
    def __init__(self, token: str, api_base_url: str = "http://localhost:5002"):
        self.token = token
        self.api_base_url = api_base_url
        self.user_sessions = {}
        
        # URL для Mini App
        self.mini_app_url = "http://localhost:8080/telegram_mini_app.html"
        
        # Создаем приложение
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        
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
🎯 **Добро пожаловать в систему подачи заявок!**

Привет, {user.first_name}! 👋

🚀 **Возможности бота:**
• ✈️ Подача заявок через веб-приложение
• 📋 Просмотр статуса заявок
• 📅 Информация о периодах подачи
• 📊 Статистика системы

**Нажмите "✈️ Подать заявку" для начала работы**
"""
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
📖 **Справка по использованию бота**

**Основные команды:**
• `/start` - Главное меню
• `/help` - Эта справка  
• `/status` - Статус системы
• `/links` - Полезные ссылки

**Как подать заявку:**
1. Нажмите "✈️ Подать заявку"
2. Заполните форму в веб-приложении
3. Проверьте данные и отправьте

**Особенности Mini App:**
• 📱 Оптимизировано для мобильных
• 🎨 Тема адаптируется под Telegram
• ✅ Автоматическая валидация
• 🔄 Заполнение данных из профиля

**Поддержка:**
При проблемах обратитесь к администратору
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
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status_text = f"""
🟢 **Система работает нормально**

📊 **Информация:**
• Приложение: {data.get('app_name', 'N/A')}
• Версия: {data.get('version', 'N/A')}
• Пользователей: {data.get('active_users', 'N/A')}
• Время: {data.get('timestamp', 'N/A')[:19]}

✅ Все сервисы доступны
🔗 API: {self.api_base_url}
📱 Mini App: {self.mini_app_url}
"""
            else:
                status_text = "🔴 **Система недоступна**\n\nПопробуйте позже."
        except Exception as e:
            status_text = f"❌ **Ошибка подключения**\n\nДетали: `{str(e)}`"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def links_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /links"""
        links_text = """
🔗 **Полезные ссылки**

**Веб-интерфейсы:**
• [Главная навигация](http://localhost:8080/index.html)
• [Форма заявки ПК](http://localhost:8080/flight_booking_ui.html)
• [Мобильная версия](http://localhost:8080/mobile_booking_ui.html)
• [Админ панель](http://localhost:8080/admin_panel.html)

**API Endpoints:**
• [Health Check](http://localhost:5002/health)
• [Статистика](http://localhost:5002/api/statistics)

⚠️ **Внимание:** Ссылки работают только при запущенных серверах
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Mini App", web_app=WebAppInfo(url=self.mini_app_url))],
            [InlineKeyboardButton("◀️ Назад в меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            links_text,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "main_menu":
            await self.show_main_menu(query)
        elif query.data == "my_applications":
            await self.show_my_applications(query)
        elif query.data == "periods":
            await self.show_periods(query)
        elif query.data == "help":
            await self.show_help(query)
        elif query.data == "statistics":
            await self.show_statistics(query)
    
    async def show_main_menu(self, query):
        """Главное меню"""
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
        
        await query.edit_message_text(
            "🎯 **Система подачи заявок**\n\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_my_applications(self, query):
        """Заявки пользователя"""
        try:
            response = requests.get(f"{self.api_base_url}/api/statistics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                text = "📋 **Статистика заявок**\n\n"
                
                if 'statistics' in data:
                    total = sum(data['statistics'].values())
                    text += f"📈 **Всего заявок:** {total}\n\n**По ОКЭ:**\n"
                    for oke, count in data['statistics'].items():
                        text += f"• {oke}: {count}\n"
                else:
                    text += "Данные временно недоступны"
            else:
                text = "❌ Не удалось получить данные"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_periods(self, query):
        """Периоды подачи заявок"""
        try:
            response = requests.get(f"{self.api_base_url}/api/application-periods", timeout=5)
            if response.status_code == 200:
                data = response.json()
                text = "📅 **Периоды подачи заявок**\n\n"
                
                if data.get('periods'):
                    for period in data['periods']:
                        status = "🟢 Активен" if period.get('is_active') else "🔴 Неактивен"
                        text += f"**{period.get('name', 'Период')}**\n"
                        text += f"{period.get('start_date')} - {period.get('end_date')}\n"
                        text += f"{status}\n\n"
                else:
                    text += "Периоды не настроены"
            else:
                text = "❌ Не удалось получить данные о периодах"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_help(self, query):
        """Справка"""
        help_text = """
📖 **Справка**

**Команды:**
• `/start` - Главное меню
• `/help` - Справка
• `/status` - Статус системы
• `/links` - Полезные ссылки

**Mini App:**
Нажмите "✈️ Подать заявку" для открытия веб-приложения с пошаговой формой.

**Поддержка:**
При проблемах обратитесь к администратору системы.
"""
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_statistics(self, query):
        """Статистика"""
        try:
            response = requests.get(f"{self.api_base_url}/api/statistics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                text = "📊 **Статистика системы**\n\n"
                
                if 'statistics' in data:
                    total = sum(data['statistics'].values())
                    text += f"📈 **Общее количество заявок:** {total}\n\n"
                    
                    if total > 0:
                        text += "**Распределение по ОКЭ:**\n"
                        for oke, count in sorted(data['statistics'].items(), key=lambda x: x[1], reverse=True):
                            percentage = (count / total * 100)
                            bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
                            text += f"{oke}: {count} ({percentage:.1f}%)\n`{bar}`\n"
                else:
                    text += "Данные недоступны"
            else:
                text = "❌ Не удалось получить статистику"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        await update.message.reply_text(
            "👋 Привет! Используйте команды или кнопки для взаимодействия.\n\n"
            "Введите /start для главного меню или /help для справки."
        )
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("links", self.links_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def run(self):
        """Запуск бота"""
        logger.info("🤖 Telegram бот запускается...")
        logger.info(f"📱 Mini App URL: {self.mini_app_url}")
        logger.info(f"🔗 API URL: {self.api_base_url}")
        
        try:
            self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске: {e}")
            raise

def main():
    """Главная функция"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Ошибка: Не установлен TELEGRAM_BOT_TOKEN")
        print("\n📋 Инструкция:")
        print("1. Создайте бота через @BotFather")
        print("2. Получите токен")
        print("3. Установите переменную: export TELEGRAM_BOT_TOKEN='токен'")
        return
    
    # Тестируем токен
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if response.status_code != 200:
            print("❌ Неверный токен бота!")
            return
        
        bot_info = response.json()['result']
        print(f"✅ Бот настроен: @{bot_info['username']} ({bot_info['first_name']})")
    except Exception as e:
        print(f"❌ Ошибка проверки токена: {e}")
        return
    
    # Создаем и запускаем бота
    bot = FlightBookingBotSimple(token)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
