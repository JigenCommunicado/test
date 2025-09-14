#!/usr/bin/env python3
"""
Менеджер конфигурации для Express Bot
Управление настройками через JSON файл
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Менеджер конфигурации бота"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Конфигурация загружена из {self.config_file}")
            else:
                logger.warning(f"Файл конфигурации {self.config_file} не найден, создаю по умолчанию")
                self.create_default_config()
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            self.create_default_config()
        
        return self.config
    
    def save_config(self) -> bool:
        """Сохранение конфигурации в файл"""
        try:
            # Создаем резервную копию
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.config_file, backup_file)
                logger.info(f"Создана резервная копия: {backup_file}")
            
            # Сохраняем новую конфигурацию
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Конфигурация сохранена в {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def create_default_config(self):
        """Создание конфигурации по умолчанию"""
        self.config = {
            "bot_settings": {
                "bot_name": "Flight Booking Bot",
                "bot_description": "Бот для подачи заявок на командировочные рейсы",
                "api_base_url": "http://localhost:5002",
                "bot_id": "00c46d64-1127-5a96-812d-3d8b27c58b99",
                "secret_key": "a75b4cd97d9e88e543f077178b2d5a4f"
            },
            "directions": {
                "МСК": ["Анадырь", "Благовещенск", "Владивосток", "Красноярск", "Магадан"],
                "СПБ": ["Волгоград", "Красноярск", "Москва", "Самара", "Сочи"],
                "Красноярск": ["Владивосток", "Сочи", "Южно-Сахалинск", "Хабаровск"],
                "Сочи": []
            },
            "oke_by_location": {
                "МСК": ["ОКЭ 1", "ОКЭ 2", "ОКЭ 3", "ОЛСиТ"],
                "СПБ": ["ОКЭ 4", "ОКЭ 5", "ОЛСиТ"],
                "Красноярск": ["ОКЭ Красноярск", "ОЛСиТ"],
                "Сочи": ["ОКЭ Сочи", "ОЛСиТ"]
            },
            "positions": ["БП", "БП BS", "СБЭ", "ИПБ"],
            "application_periods": {
                "enabled": True,
                "start_day": 20,
                "end_day": 5,
                "working_hours": {"start": "09:00", "end": "18:00"},
                "exceptions": []
            },
            "notifications": {
                "enabled": True,
                "templates": {
                    "application_submitted": "Ваша заявка на рейс успешно подана!",
                    "application_reminder": "Напоминание: не забудьте подать заявку на рейс",
                    "period_opening": "Открыт прием заявок на рейсы на следующий месяц"
                }
            },
            "system": {
                "log_level": "INFO",
                "max_log_size": "10MB",
                "backup_enabled": True,
                "auto_restart": False
            }
        }
        self.save_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения по ключу (поддерживает вложенные ключи через точку)"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Установка значения по ключу (поддерживает вложенные ключи через точку)"""
        keys = key.split('.')
        config = self.config
        
        try:
            # Проходим по всем ключам кроме последнего
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Устанавливаем значение
            config[keys[-1]] = value
            return True
        except Exception as e:
            logger.error(f"Ошибка установки значения {key}: {e}")
            return False
    
    def get_directions(self, location: str) -> list:
        """Получение направлений для локации"""
        return self.get(f"directions.{location}", [])
    
    def add_direction(self, location: str, direction: str) -> bool:
        """Добавление направления для локации"""
        directions = self.get_directions(location)
        if direction not in directions:
            directions.append(direction)
            return self.set(f"directions.{location}", directions)
        return False
    
    def remove_direction(self, location: str, direction: str) -> bool:
        """Удаление направления для локации"""
        directions = self.get_directions(location)
        if direction in directions:
            directions.remove(direction)
            return self.set(f"directions.{location}", directions)
        return False
    
    def get_oke(self, location: str) -> list:
        """Получение ОКЭ для локации"""
        return self.get(f"oke_by_location.{location}", [])
    
    def add_oke(self, location: str, oke: str) -> bool:
        """Добавление ОКЭ для локации"""
        oke_list = self.get_oke(location)
        if oke not in oke_list:
            oke_list.append(oke)
            return self.set(f"oke_by_location.{location}", oke_list)
        return False
    
    def remove_oke(self, location: str, oke: str) -> bool:
        """Удаление ОКЭ для локации"""
        oke_list = self.get_oke(location)
        if oke in oke_list:
            oke_list.remove(oke)
            return self.set(f"oke_by_location.{location}", oke_list)
        return False
    
    def get_positions(self) -> list:
        """Получение списка должностей"""
        return self.get("positions", [])
    
    def add_position(self, position: str) -> bool:
        """Добавление должности"""
        positions = self.get_positions()
        if position not in positions:
            positions.append(position)
            return self.set("positions", positions)
        return False
    
    def remove_position(self, position: str) -> bool:
        """Удаление должности"""
        positions = self.get_positions()
        if position in positions:
            positions.remove(position)
            return self.set("positions", positions)
        return False
    
    def validate_config(self) -> Dict[str, list]:
        """Валидация конфигурации"""
        errors = []
        warnings = []
        
        # Проверяем обязательные поля
        required_fields = [
            "bot_settings.bot_name",
            "bot_settings.bot_description",
            "bot_settings.api_base_url",
            "bot_settings.bot_id",
            "bot_settings.secret_key"
        ]
        
        for field in required_fields:
            if not self.get(field):
                errors.append(f"Обязательное поле {field} не заполнено")
        
        # Проверяем направления
        directions = self.get("directions", {})
        if not directions:
            warnings.append("Не настроены направления")
        
        # Проверяем ОКЭ
        oke = self.get("oke_by_location", {})
        if not oke:
            warnings.append("Не настроены ОКЭ")
        
        # Проверяем должности
        positions = self.get("positions", [])
        if not positions:
            warnings.append("Не настроены должности")
        
        return {"errors": errors, "warnings": warnings}
    
    def get_backup_files(self) -> list:
        """Получение списка файлов резервных копий"""
        backup_files = []
        config_dir = os.path.dirname(self.config_file)
        
        if os.path.exists(config_dir):
            for file in os.listdir(config_dir):
                if file.startswith(os.path.basename(self.config_file) + ".backup."):
                    file_path = os.path.join(config_dir, file)
                    stat = os.stat(file_path)
                    backup_files.append({
                        "filename": file,
                        "path": file_path,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "size": stat.st_size
                    })
        
        return sorted(backup_files, key=lambda x: x["created"], reverse=True)
    
    def restore_backup(self, backup_file: str) -> bool:
        """Восстановление из резервной копии"""
        try:
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_config = json.load(f)
                
                # Создаем резервную копию текущей конфигурации
                self.save_config()
                
                # Восстанавливаем из backup
                self.config = backup_config
                return self.save_config()
            return False
        except Exception as e:
            logger.error(f"Ошибка восстановления из backup {backup_file}: {e}")
            return False

# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()
