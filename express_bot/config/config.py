#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

class Config:
    """Конфигурация Express Bot"""
    
    # Данные бота
    BOT_ID = os.getenv('BOT_ID', '00c46d64-1127-5a96-812d-3d8b27c58b99')
    SECRET_KEY = os.getenv('SECRET_KEY', 'a75b4cd97d9e88e543f077178b2d5a4f')
    BOTX_URL = os.getenv('BOTX_URL', 'https://cts.express.ms')
    
    # Настройки Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    PORT = int(os.getenv('PORT', 5000))
    
    # Настройки логирования
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Проверка корректности конфигурации"""
        if not cls.BOT_ID:
            raise ValueError("BOT_ID не установлен")
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY не установлен")
        return True
