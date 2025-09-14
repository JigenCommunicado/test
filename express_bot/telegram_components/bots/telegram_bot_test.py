"""
Тестовая версия Telegram бота без Mini App
Для демонстрации основного функционала
"""

import os
import json
import logging
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

class FlightBookingBotTest:
    """Тестовая версия Telegram бота"""
    
    def __init__(self, token: str, api_base_url: str = "http://localhost:5002"):
        self.token = token
        self.api_base_url = api_base_url
        self.user_sessions = {}
        
        # Создаем приложение
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Информация", callback_data="info"),
                InlineKeyboardButton("📊 Статистика", callback_data="statistics")
            ],
            [
                InlineKeyboardButton("📅 Периоды", callback_data="periods"),
                InlineKeyboardButton("🔗 Ссылки", callback_data="links")
            ],
            [
                InlineKeyboardButton("🌐 Ссылки", callback_data="links"),
                InlineKeyboardButton("🔧 Статус системы", callback_data="status")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎯 **Express SmartApp - Система подачи заявок**

Привет, {user.first_name}! 👋

🤖 **Это тестовая версия бота**

**Доступные функции:**
• 📊 Просмотр статистики системы
• 📅 Информация о периодах подачи заявок
• 🔧 Проверка статуса серверов
• 🔗 Ссылки на веб-интерфейсы

**Для подачи заявки используйте веб-версию:**
• 🖥️ ПК: http://localhost:8080/flight_booking_ui.html
• 📱 Мобильная: http://localhost:8080/mobile_booking_ui.html

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
📖 **Справка по использованию тестового бота**

**Команды:**
• `/start` - Главное меню
• `/help` - Эта справка  
• `/status` - Быстрая проверка статуса
• `/stats` - Быстрая статистика
• `/links` - Полезные ссылки

**Описание функций:**
• **Статистика** - количество заявок по ОКЭ
• **Периоды** - активные периоды подачи заявок
• **Статус** - проверка работы API и серверов
• **Ссылки** - быстрый доступ к веб-интерфейсам

**Ограничения тестовой версии:**
❌ Подача заявок через бота недоступна
❌ Mini App требует HTTPS для работы
✅ Просмотр данных работает
✅ Интеграция с API работает

**Для полного функционала:**
Используйте веб-интерфейсы по ссылкам в разделе "🔗 Ссылки"
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
        await self.show_status_inline(update, is_command=True)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats"""
        await self.show_statistics_inline(update, is_command=True)
    
    async def links_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /links"""
        await self.show_links_inline(update, is_command=True)
    
    async def show_status_inline(self, update_or_query, is_command=False):
        """Показать статус системы"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status_text = f"""
🟢 **Система работает отлично!**

📊 **Информация:**
• Приложение: {data.get('app_name', 'N/A')}
• Версия: {data.get('version', 'N/A')}
• Пользователей: {data.get('active_users', 'N/A')}
• Время: {data.get('timestamp', 'N/A')[:19]}

🔗 **Сервисы:**
✅ Flask API (порт 5002)
✅ Static Server (порт 8080)
✅ Telegram Bot

**Endpoints:**
• Health: {self.api_base_url}/health
• Statistics: {self.api_base_url}/api/statistics
• Web UI: http://localhost:8080/
"""
            else:
                status_text = "🔴 **Система недоступна**\n\nAPI сервер не отвечает."
        except Exception as e:
            status_text = f"❌ **Ошибка подключения к API**\n\n`{str(e)}`\n\nПроверьте что Flask сервер запущен на порту 5002"
        
        keyboard = [[InlineKeyboardButton("🔄 Обновить", callback_data="status")]]
        if not is_command:
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_command:
            await update_or_query.message.reply_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update_or_query.edit_message_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def show_statistics_inline(self, update_or_query, is_command=False):
        """Показать статистику"""
        try:
            response = requests.get(f"{self.api_base_url}/api/statistics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                text = "📊 **Статистика системы**\n\n"
                
                if 'statistics' in data and data['statistics']:
                    stats = data['statistics']
                    
                    # Получаем общее количество из API или вычисляем
                    total = stats.get('total_applications', 0)
                    if total == 0 and 'by_oke' in stats:
                        total = sum(stats['by_oke'].values())
                    
                    text += f"📈 **Общее количество заявок:** {total}\n"
                    if 'total_files' in stats:
                        text += f"📂 **Файлов Excel:** {stats['total_files']}\n"
                    text += "\n"
                    
                    if total > 0 and 'by_oke' in stats and stats['by_oke']:
                        text += "**Распределение по ОКЭ:**\n"
                        for oke, count in sorted(stats['by_oke'].items(), key=lambda x: x[1], reverse=True):
                            percentage = (count / total * 100)
                            # Простой текстовый прогресс-бар
                            bar_length = int(percentage / 10)
                            bar = "█" * bar_length + "░" * (10 - bar_length)
                            text += f"`{bar}` {oke}: {count} ({percentage:.1f}%)\n"
                    else:
                        text += "Заявок пока нет"
                else:
                    text += "📝 **Заявок пока нет**\n\nСистема готова к приему заявок через веб-интерфейс."
            else:
                text = "❌ Не удалось получить статистику\n\nAPI сервер недоступен."
        except Exception as e:
            text = f"❌ **Ошибка получения статистики**\n\n`{str(e)}`"
        
        keyboard = [[InlineKeyboardButton("🔄 Обновить", callback_data="statistics")]]
        if not is_command:
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_command:
            await update_or_query.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update_or_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def show_links_inline(self, update_or_query, is_command=False):
        """Показать ссылки"""
        links_text = """
🔗 **Информация о системе**

**🌐 Веб-интерфейсы доступны:**
• 🏠 Главная навигация: `localhost:8080/index.html`
• ✈️ Форма заявки (ПК): `localhost:8080/flight_booking_ui.html`
• 📱 Мобильная версия: `localhost:8080/mobile_booking_ui.html`
• 🎛️ Админ панель: `localhost:8080/admin_panel.html`

**🔧 API Endpoints:**
• 💚 Health Check: `localhost:5002/health`
• 📊 Статистика: `localhost:5002/api/statistics`
• 📅 Периоды: `localhost:5002/api/application-periods`

**📱 Для мобильных:**
• Откройте мобильную версию в браузере
• Добавьте в закладки для быстрого доступа
• Работает как веб-приложение (PWA)

⚠️ **Внимание:** 
• Ссылки работают только при запущенных серверах
• Для Mini App в Telegram нужен HTTPS
• Локальные ссылки работают только на том же устройстве
"""
        
        keyboard = []
        if not is_command:
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        if is_command:
            await update_or_query.message.reply_text(
                links_text,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            await update_or_query.edit_message_text(
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
        elif query.data == "info":
            await self.show_info(query)
        elif query.data == "statistics":
            await self.show_statistics_inline(query)
        elif query.data == "periods":
            await self.show_periods(query)
        elif query.data == "links":
            await self.show_links_inline(query)
        elif query.data == "status":
            await self.show_status_inline(query)
    
    async def show_main_menu(self, query):
        """Главное меню"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Информация", callback_data="info"),
                InlineKeyboardButton("📊 Статистика", callback_data="statistics")
            ],
            [
                InlineKeyboardButton("📅 Периоды", callback_data="periods"),
                InlineKeyboardButton("🔗 Ссылки", callback_data="links")
            ],
            [
                InlineKeyboardButton("🌐 Ссылки", callback_data="links"),
                InlineKeyboardButton("🔧 Статус системы", callback_data="status")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎯 **Express SmartApp - Главное меню**\n\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_info(self, query):
        """Информация о системе"""
        info_text = """
📋 **О системе Express SmartApp**

🎯 **Назначение:**
Система для подачи заявок на корпоративные рейсы

✨ **Основные возможности:**
• Подача заявок через веб-форму
• Управление периодами подачи заявок
• Система уведомлений
• Статистика и аналитика
• Админ панель для управления
• Telegram бот для мониторинга

🏗️ **Архитектура:**
• **Backend:** Flask API (Python)
• **Frontend:** HTML/CSS/JavaScript
• **Data:** Excel интеграция
• **Bot:** Python Telegram Bot
• **Servers:** HTTP Static + Flask API

🔧 **Технические детали:**
• Flask API сервер: порт 5002
• Статический сервер: порт 8080
• База данных: Excel файлы
• Уведомления: встроенная система

📱 **Интерфейсы:**
• ПК версия с полным функционалом
• Мобильная адаптивная версия
• Telegram бот (мониторинг)
• Админ панель

🚀 **Статус:** Полностью функциональна
"""
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            info_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_periods(self, query):
        """Периоды подачи заявок"""
        try:
            response = requests.get(f"{self.api_base_url}/api/public/application-periods", timeout=5)
            if response.status_code == 200:
                data = response.json()
                text = "📅 **Периоды подачи заявок**\n\n"
                
                if data.get('periods'):
                    for i, period in enumerate(data['periods'], 1):
                        status = "🟢 Активен" if period.get('is_active') else "🔴 Неактивен"
                        text += f"**{i}. {period.get('name', 'Период без названия')}**\n"
                        text += f"📅 {period.get('start_date', 'N/A')} - {period.get('end_date', 'N/A')}\n"
                        text += f"📊 {status}\n"
                        if period.get('description'):
                            text += f"📝 {period['description']}\n"
                        text += "\n"
                else:
                    text += "📝 **Периоды не настроены**\n\n"
                    text += "Обратитесь к администратору для настройки периодов подачи заявок."
            elif response.status_code == 401:
                text = "🔐 **Требуется авторизация**\n\n"
                text += "Данный endpoint требует авторизации.\n"
                text += "Периоды заявок можно просмотреть через:\n"
                text += "• [Админ панель](http://localhost:8080/admin_panel.html)\n"
                text += "• [Управление периодами](http://localhost:8080/application_periods.html)\n\n"
                text += "**Альтернативный функционал:**\n"
                text += "Используйте веб-интерфейс для полного доступа к настройкам периодов."
            else:
                text = f"❌ **Ошибка API: {response.status_code}**\n\n"
                text += "Для просмотра периодов используйте:\n"
                text += "• [Админ панель](http://localhost:8080/admin_panel.html)\n"
                text += "• [Управление периодами](http://localhost:8080/application_periods.html)"
        except Exception as e:
            text = f"❌ **Ошибка подключения**\n\n`{str(e)}`\n\n"
            text += "**Альтернативные способы:**\n"
            text += "• [Админ панель](http://localhost:8080/admin_panel.html)\n"
            text += "• [Управление периодами](http://localhost:8080/application_periods.html)"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="periods")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        help_text = """
👋 **Привет!** 

Я тестовый бот системы Express SmartApp.

🤖 **Доступные команды:**
• `/start` - Главное меню
• `/help` - Справка
• `/status` - Статус системы
• `/stats` - Статистика
• `/links` - Полезные ссылки

**Для подачи заявок используйте веб-интерфейс по ссылке /links**
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка данных от Web App"""
        try:
            import json
            data = json.loads(update.effective_message.web_app_data.data)
            user = update.effective_user
            
            logger.info(f"Получены данные от Web App от {user.first_name}: {data}")
            
            if data.get('action') == 'submit_application':
                app_data = data.get('data', {})
                
                # Отправляем данные в Flask API
                try:
                    response = requests.post(
                        f"{self.api_base_url}/api/application",
                        json=app_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            await update.effective_message.reply_text(
                                "✅ Заявка успешно отправлена!\n\n"
                                f"📋 Данные заявки:\n"
                                f"• Локация: {app_data.get('location', 'Не указано')}\n"
                                f"• ОКЭ: {app_data.get('oke', 'Не указано')}\n"
                                f"• Дата: {app_data.get('date', 'Не указано')}\n"
                                f"• ФИО: {app_data.get('fio', 'Не указано')}\n"
                                f"• Направление: {app_data.get('direction', 'Не указано')}\n\n"
                                f"Заявка будет обработана в ближайшее время."
                            )
                        else:
                            await update.effective_message.reply_text(
                                f"❌ Ошибка при отправке заявки:\n{result.get('error', 'Неизвестная ошибка')}"
                            )
                    else:
                        await update.effective_message.reply_text(
                            f"❌ Ошибка сервера при отправке заявки (код: {response.status_code})"
                        )
                        
                except requests.RequestException as e:
                    logger.error(f"Ошибка при отправке заявки через Web App: {e}")
                    await update.effective_message.reply_text(
                        "❌ Ошибка соединения с сервером при отправке заявки.\n"
                        "Попробуйте позже или свяжитесь с администратором."
                    )
            else:
                await update.effective_message.reply_text("📱 Данные от Web App получены, но неизвестного типа.")
                
        except Exception as e:
            logger.error(f"Ошибка обработки данных Web App: {e}")
            await update.effective_message.reply_text(
                "❌ Ошибка при обработке данных от Mini App."
            )

    def setup_handlers(self):
        """Настройка обработчиков"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("links", self.links_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def run(self):
        """Запуск бота"""
        logger.info("🤖 Тестовый Telegram бот запускается...")
        logger.info(f"🔗 API URL: {self.api_base_url}")
        logger.info("📱 Mini App отключен (требует HTTPS)")
        
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
        print("export TELEGRAM_BOT_TOKEN='ваш_токен'")
        return
    
    # Тестируем токен
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if response.status_code != 200:
            print("❌ Неверный токен бота!")
            return
        
        bot_info = response.json()['result']
        print(f"✅ Бот подключен: @{bot_info['username']} ({bot_info['first_name']})")
        print("🔗 Найдите бота в Telegram и отправьте /start")
    except Exception as e:
        print(f"❌ Ошибка проверки токена: {e}")
        return
    
    # Создаем и запускаем бота
    bot = FlightBookingBotTest(token)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
