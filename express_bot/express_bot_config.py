#!/usr/bin/env python3
"""
Конфигурация Express Bot
"""

import os
from typing import Dict, Any

# Конфигурация Express Bot
EXPRESS_BOT_CONFIG = {
    # Основные настройки бота
    'bot_id': os.environ.get('EXPRESS_BOT_ID', '00c46d64-1127-5a96-812d-3d8b27c58b99'),
    'secret_key': os.environ.get('EXPRESS_SECRET_KEY', 'a75b4cd97d9e88e543f077178b2d5a4f'),
    'bot_name': 'Flight Booking Bot',
    'bot_description': 'Бот для подачи заявок на командировочные рейсы',
    
    # API настройки
    'api_base_url': os.environ.get('FLASK_API_URL', 'http://localhost:5002'),
    'webhook_url': os.environ.get('WEBHOOK_URL', 'https://jill-lips-jon-productive.trycloudflare.com/webhook'),
    
    # Настройки сервера
    'host': '0.0.0.0',
    'port': int(os.environ.get('BOT_PORT', 5006)),
    
    # Настройки логирования
    'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
    'log_file': os.environ.get('LOG_FILE', 'express_bot.log'),
    
    # Настройки сессий
    'session_timeout': int(os.environ.get('SESSION_TIMEOUT', 3600)),  # 1 час
    'max_sessions': int(os.environ.get('MAX_SESSIONS', 1000)),
    
    # Настройки API
    'api_timeout': int(os.environ.get('API_TIMEOUT', 30)),
    'max_retries': int(os.environ.get('MAX_RETRIES', 3)),
}

# Настройки для Express сервера
EXPRESS_SERVER_CONFIG = {
    'smartapps': [
        {
            'name': EXPRESS_BOT_CONFIG['bot_name'],
            'url': EXPRESS_BOT_CONFIG['webhook_url'].replace('/webhook', '/'),
            'manifest_url': f"{EXPRESS_BOT_CONFIG['webhook_url'].replace('/webhook', '')}/manifest",
            'webhook_url': EXPRESS_BOT_CONFIG['webhook_url'],
            'icon': '✈️',
            'color': '#0088cc',
            'permissions': [
                'read_user_info',
                'send_messages',
                'access_files'
            ]
        }
    ]
}

def get_config() -> Dict[str, Any]:
    """Получить конфигурацию бота"""
    return EXPRESS_BOT_CONFIG

def get_server_config() -> Dict[str, Any]:
    """Получить конфигурацию для Express сервера"""
    return EXPRESS_SERVER_CONFIG

def validate_config() -> bool:
    """Проверить корректность конфигурации"""
    required_fields = ['bot_id', 'secret_key', 'api_base_url', 'webhook_url']
    
    for field in required_fields:
        if not EXPRESS_BOT_CONFIG.get(field):
            print(f"❌ Отсутствует обязательное поле: {field}")
            return False
    
    return True

if __name__ == "__main__":
    if validate_config():
        print("✅ Конфигурация корректна")
        print(f"🤖 Bot ID: {EXPRESS_BOT_CONFIG['bot_id']}")
        print(f"🔗 Webhook URL: {EXPRESS_BOT_CONFIG['webhook_url']}")
        print(f"📡 API URL: {EXPRESS_BOT_CONFIG['api_base_url']}")
    else:
        print("❌ Конфигурация содержит ошибки")
