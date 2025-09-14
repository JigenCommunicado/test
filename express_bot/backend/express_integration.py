"""
Модуль интеграции с Express мессенджером
Включает webhook для получения сообщений, API для отправки уведомлений и интеграцию с ботом
"""

import json
import logging
import time
import hashlib
import hmac
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from flask import request, jsonify

logger = logging.getLogger(__name__)

@dataclass
class ExpressMessage:
    """Структура сообщения от Express мессенджера"""
    message_id: str
    user_id: str
    chat_id: str
    text: str
    timestamp: datetime
    message_type: str = "text"
    attachments: List[Dict] = None

@dataclass
class ExpressUser:
    """Структура пользователя Express мессенджера"""
    user_id: str
    username: str
    first_name: str
    last_name: str
    language_code: str = "ru"
    is_bot: bool = False

class ExpressWebhookHandler:
    """Обработчик webhook от Express мессенджера"""
    
    def __init__(self, webhook_secret: str = None):
        self.webhook_secret = webhook_secret
        self.message_handlers = {}
        
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Проверка подписи webhook"""
        if not self.webhook_secret:
            return True  # Если секрет не установлен, пропускаем проверку
            
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def parse_message(self, data: Dict) -> Optional[ExpressMessage]:
        """Парсинг сообщения от Express"""
        try:
            message_data = data.get('message', {})
            if not message_data:
                return None
                
            return ExpressMessage(
                message_id=str(message_data.get('message_id', '')),
                user_id=str(message_data.get('from', {}).get('id', '')),
                chat_id=str(message_data.get('chat', {}).get('id', '')),
                text=message_data.get('text', ''),
                timestamp=datetime.fromtimestamp(message_data.get('date', 0)),
                message_type=message_data.get('type', 'text'),
                attachments=message_data.get('attachments', [])
            )
        except Exception as e:
            logger.error(f"Ошибка парсинга сообщения: {e}")
            return None
    
    def register_handler(self, command: str, handler_func):
        """Регистрация обработчика команды"""
        self.message_handlers[command.lower()] = handler_func
        logger.info(f"Зарегистрирован обработчик для команды: {command}")
    
    def handle_message(self, message: ExpressMessage) -> Dict:
        """Обработка входящего сообщения"""
        try:
            text = message.text.strip()
            
            # Обработка команд
            if text.startswith('/'):
                command = text.split()[0].lower()
                if command in self.message_handlers:
                    return self.message_handlers[command](message)
                else:
                    return self._unknown_command_response(message)
            
            # Обработка обычных сообщений
            return self._handle_text_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return {"error": "Внутренняя ошибка сервера"}
    
    def _unknown_command_response(self, message: ExpressMessage) -> Dict:
        """Ответ на неизвестную команду"""
        return {
            "method": "sendMessage",
            "chat_id": message.chat_id,
            "text": "❌ Неизвестная команда. Используйте /help для списка доступных команд."
        }
    
    def _handle_text_message(self, message: ExpressMessage) -> Dict:
        """Обработка обычного текстового сообщения"""
        return {
            "method": "sendMessage",
            "chat_id": message.chat_id,
            "text": f"👋 Привет! Я бот для подачи заявок на корпоративные рейсы.\n\nИспользуйте /help для списка команд."
        }

class ExpressBot:
    """Бот для Express мессенджера"""
    
    def __init__(self, bot_token: str, api_url: str = "https://api.express-messenger.com"):
        self.bot_token = bot_token
        self.api_url = api_url
        self.webhook_handler = ExpressWebhookHandler()
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Регистрация стандартных обработчиков команд"""
        self.webhook_handler.register_handler('/start', self._handle_start)
        self.webhook_handler.register_handler('/help', self._handle_help)
        self.webhook_handler.register_handler('/status', self._handle_status)
        self.webhook_handler.register_handler('/application', self._handle_application)
        self.webhook_handler.register_handler('/my_applications', self._handle_my_applications)
        self.webhook_handler.register_handler('/periods', self._handle_periods)
        
    def _handle_start(self, message: ExpressMessage) -> Dict:
        """Обработка команды /start"""
        return {
            "method": "sendMessage",
            "chat_id": message.chat_id,
            "text": """🚀 Добро пожаловать в Express SmartApp!

Я помогу вам подать заявку на корпоративный рейс.

📋 Доступные команды:
/help - Список команд
/application - Подать заявку
/my_applications - Мои заявки
/periods - Периоды подачи заявок
/status - Статус системы

Для начала работы используйте /application"""
        }
    
    def _handle_help(self, message: ExpressMessage) -> Dict:
        """Обработка команды /help"""
        return {
            "method": "sendMessage",
            "chat_id": message.chat_id,
            "text": """📋 Список команд Express SmartApp:

🚀 /start - Начать работу с ботом
📝 /application - Подать заявку на рейс
📊 /my_applications - Просмотреть мои заявки
📅 /periods - Информация о периодах подачи заявок
⚡ /status - Статус системы
❓ /help - Показать это сообщение

💡 Для подачи заявки используйте /application"""
        }
    
    def _handle_status(self, message: ExpressMessage) -> Dict:
        """Обработка команды /status"""
        try:
            # Проверяем статус системы
            status = "🟢 Система работает нормально"
            
            return {
                "method": "sendMessage",
                "chat_id": message.chat_id,
                "text": f"""⚡ Статус системы:

{status}

🕐 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
📊 Сервер: Express SmartApp v1.0.0"""
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса: {e}")
            return {
                "method": "sendMessage",
                "chat_id": message.chat_id,
                "text": "❌ Ошибка получения статуса системы"
            }
    
    def _handle_application(self, message: ExpressMessage) -> Dict:
        """Обработка команды /application"""
        return {
            "method": "sendMessage",
            "chat_id": message.chat_id,
            "text": """📝 Подача заявки на корпоративный рейс:

Для подачи заявки перейдите по ссылке:
🌐 https://your-domain.com/flight_booking_ui.html

Или используйте мобильную версию:
📱 https://your-domain.com/mobile_booking_ui.html

💡 В форме выберите:
• Локацию (Москва, СПб, Красноярск, Сочи)
• ОКЭ
• Дату рейса
• Должность
• Направление
• Пожелания

После заполнения заявка будет автоматически сохранена!"""
        }
    
    def _handle_my_applications(self, message: ExpressMessage) -> Dict:
        """Обработка команды /my_applications"""
        try:
            # Здесь можно добавить логику получения заявок пользователя
            return {
                "method": "sendMessage",
                "chat_id": message.chat_id,
                "text": """📊 Ваши заявки:

Для просмотра ваших заявок перейдите в админ панель:
🔧 https://your-domain.com/admin_panel.html

Или используйте поиск:
🔍 https://your-domain.com/search_interface.html

💡 В будущих версиях заявки будут отображаться прямо в чате!"""
            }
        except Exception as e:
            logger.error(f"Ошибка получения заявок: {e}")
            return {
                "method": "sendMessage",
                "chat_id": message.chat_id,
                "text": "❌ Ошибка получения ваших заявок"
            }
    
    def _handle_periods(self, message: ExpressMessage) -> Dict:
        """Обработка команды /periods"""
        try:
            # Здесь можно добавить логику получения периодов
            return {
                "method": "sendMessage",
                "chat_id": message.chat_id,
                "text": """📅 Периоды подачи заявок:

Для просмотра и управления периодами:
🗓️ https://your-domain.com/application_periods.html

💡 Активные периоды отображаются в админ панели"""
            }
        except Exception as e:
            logger.error(f"Ошибка получения периодов: {e}")
            return {
                "method": "sendMessage",
                "chat_id": message.chat_id,
                "text": "❌ Ошибка получения информации о периодах"
            }
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Отправка сообщения пользователю"""
        try:
            url = f"{self.api_url}/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    def send_notification(self, user_id: str, title: str, message: str) -> bool:
        """Отправка уведомления пользователю"""
        try:
            text = f"🔔 <b>{title}</b>\n\n{message}"
            return self.send_message(user_id, text)
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            return False

class ExpressNotificationService:
    """Сервис для отправки уведомлений через Express"""
    
    def __init__(self, bot: ExpressBot):
        self.bot = bot
        self.subscribers = {}  # user_id -> subscription_data
        
    def subscribe_user(self, user_id: str, chat_id: str, preferences: Dict = None):
        """Подписка пользователя на уведомления"""
        self.subscribers[user_id] = {
            "chat_id": chat_id,
            "preferences": preferences or {},
            "subscribed_at": datetime.now()
        }
        logger.info(f"Пользователь {user_id} подписан на уведомления")
    
    def unsubscribe_user(self, user_id: str):
        """Отписка пользователя от уведомлений"""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
            logger.info(f"Пользователь {user_id} отписан от уведомлений")
    
    def send_application_notification(self, user_id: str, application_data: Dict):
        """Отправка уведомления о создании заявки"""
        if user_id not in self.subscribers:
            return False
            
        title = "✅ Заявка создана"
        message = f"""Ваша заявка на корпоративный рейс успешно создана!

📋 Детали заявки:
• Локация: {application_data.get('location', 'Не указано')}
• ОКЭ: {application_data.get('oke', 'Не указано')}
• Дата: {application_data.get('date', 'Не указано')}
• Направление: {application_data.get('direction', 'Не указано')}

🆔 ID заявки: {application_data.get('application_id', 'Не указано')}"""
        
        return self.bot.send_notification(
            self.subscribers[user_id]["chat_id"],
            title,
            message
        )
    
    def send_period_notification(self, user_id: str, period_data: Dict):
        """Отправка уведомления о периоде заявок"""
        if user_id not in self.subscribers:
            return False
            
        title = "📅 Новый период заявок"
        message = f"""Открыт новый период подачи заявок!

📋 Период: {period_data.get('name', 'Не указано')}
📅 Начало: {period_data.get('start_date', 'Не указано')}
📅 Окончание: {period_data.get('end_date', 'Не указано')}

Подать заявку: /application"""
        
        return self.bot.send_notification(
            self.subscribers[user_id]["chat_id"],
            title,
            message
        )
    
    def broadcast_notification(self, title: str, message: str, user_filter: callable = None):
        """Массовая рассылка уведомлений"""
        sent_count = 0
        failed_count = 0
        
        for user_id, subscription in self.subscribers.items():
            if user_filter and not user_filter(user_id, subscription):
                continue
                
            if self.bot.send_notification(subscription["chat_id"], title, message):
                sent_count += 1
            else:
                failed_count += 1
        
        logger.info(f"Рассылка завершена: {sent_count} отправлено, {failed_count} ошибок")
        return {"sent": sent_count, "failed": failed_count}

# Глобальные экземпляры
express_bot = None
notification_service = None

def init_express_integration(bot_token: str, webhook_secret: str = None):
    """Инициализация интеграции с Express"""
    global express_bot, notification_service
    
    express_bot = ExpressBot(bot_token)
    notification_service = ExpressNotificationService(express_bot)
    
    if webhook_secret:
        express_bot.webhook_handler.webhook_secret = webhook_secret
    
    logger.info("Интеграция с Express мессенджером инициализирована")
    return express_bot, notification_service

def get_express_bot():
    """Получение экземпляра бота"""
    return express_bot

def get_notification_service():
    """Получение сервиса уведомлений"""
    return notification_service

