#!/usr/bin/env python3
"""
Express SmartApp - Правильная реализация согласно документации Express
Система подачи заявок на рейсы для российского мессенджера Express
"""

import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Конфигурация Express SmartApp согласно документации
EXPRESS_SMARTAPP_CONFIG = {
    'app_name': 'Flight Booking SmartApp',
    'app_version': '1.0.0',
    'app_description': 'Система подачи заявок на командировочные рейсы',
    'app_icon': '✈️',
    'app_color': '#0088cc',
    'api_base_url': os.environ.get('FLASK_API_URL', 'http://localhost:5002'),
    'express_server_url': os.environ.get('EXPRESS_SERVER_URL', 'http://localhost:8080')
}

class ExpressSmartApp:
    """Express SmartApp согласно официальной документации"""
    
    def __init__(self):
        self.app_name = EXPRESS_SMARTAPP_CONFIG['app_name']
        self.version = EXPRESS_SMARTAPP_CONFIG['app_version']
        self.api_url = EXPRESS_SMARTAPP_CONFIG['api_base_url']
        self.express_url = EXPRESS_SMARTAPP_CONFIG['express_server_url']
        
    def get_manifest(self):
        """Возвращает манифест SmartApp для Express"""
        return {
            "name": self.app_name,
            "version": self.version,
            "description": EXPRESS_SMARTAPP_CONFIG['app_description'],
            "icon": EXPRESS_SMARTAPP_CONFIG['app_icon'],
            "color": EXPRESS_SMARTAPP_CONFIG['app_color'],
            "author": "Express SmartApp Team",
            "permissions": [
                "read_user_info",
                "send_messages", 
                "access_files",
                "manage_applications"
            ],
            "capabilities": [
                "flight_booking",
                "application_management",
                "notifications",
                "statistics"
            ],
            "endpoints": {
                "main": "/smartapp",
                "api": "/api/smartapp",
                "webhook": "/webhook/smartapp"
            },
            "ui": {
                "type": "web",
                "responsive": True,
                "theme": "express"
            }
        }
    
    def get_main_interface(self):
        """Главный интерфейс SmartApp для Express"""
        return {
            "title": f"{EXPRESS_SMARTAPP_CONFIG['app_icon']} {self.app_name}",
            "subtitle": "Система подачи заявок на командировочные рейсы",
            "sections": [
                {
                    "id": "quick_actions",
                    "title": "Быстрые действия",
                    "type": "grid",
                    "items": [
                        {
                            "id": "new_application",
                            "title": "Подать заявку",
                            "icon": "📝",
                            "action": "open_form",
                            "color": "#2196f3"
                        },
                        {
                            "id": "my_applications", 
                            "title": "Мои заявки",
                            "icon": "📋",
                            "action": "open_list",
                            "color": "#4caf50"
                        },
                        {
                            "id": "periods",
                            "title": "Периоды",
                            "icon": "📅", 
                            "action": "open_periods",
                            "color": "#ff9800"
                        },
                        {
                            "id": "statistics",
                            "title": "Статистика",
                            "icon": "📊",
                            "action": "open_stats",
                            "color": "#9c27b0"
                        }
                    ]
                }
            ]
        }
    
    def get_application_form_config(self):
        """Конфигурация формы подачи заявки"""
        return {
            "title": "Подача заявки на рейс",
            "description": "Заполните форму для подачи заявки на командировочный рейс",
            "fields": [
                {
                    "id": "location",
                    "type": "select",
                    "label": "Локация",
                    "required": True,
                    "placeholder": "Выберите локацию",
                    "options": [
                        {"value": "Москва", "label": "Москва"},
                        {"value": "Санкт-Петербург", "label": "Санкт-Петербург"},
                        {"value": "Новосибирск", "label": "Новосибирск"},
                        {"value": "Екатеринбург", "label": "Екатеринбург"},
                        {"value": "Красноярск", "label": "Красноярск"},
                        {"value": "Сочи", "label": "Сочи"}
                    ]
                },
                {
                    "id": "oke",
                    "type": "select",
                    "label": "ОКЭ",
                    "required": True,
                    "placeholder": "Выберите ОКЭ",
                    "options": [
                        {"value": "ОКЭ 1", "label": "ОКЭ 1"},
                        {"value": "ОКЭ 2", "label": "ОКЭ 2"},
                        {"value": "ОКЭ 3", "label": "ОКЭ 3"},
                        {"value": "ОКЭ 4", "label": "ОКЭ 4"},
                        {"value": "ОКЭ 5", "label": "ОКЭ 5"},
                        {"value": "ОКЭ Красноярск", "label": "ОКЭ Красноярск"},
                        {"value": "ОКЭ Сочи", "label": "ОКЭ Сочи"},
                        {"value": "ОЛСиТ", "label": "ОЛСиТ"}
                    ]
                },
                {
                    "id": "date",
                    "type": "date",
                    "label": "Планируемая дата вылета",
                    "required": True,
                    "min_date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "id": "position",
                    "type": "select",
                    "label": "Должность",
                    "required": True,
                    "placeholder": "Выберите должность",
                    "options": [
                        {"value": "БП", "label": "БП"},
                        {"value": "РП", "label": "РП"},
                        {"value": "Специалист", "label": "Специалист"},
                        {"value": "Эксперт", "label": "Эксперт"},
                        {"value": "Руководитель", "label": "Руководитель"}
                    ]
                },
                {
                    "id": "fio",
                    "type": "text",
                    "label": "ФИО",
                    "required": True,
                    "placeholder": "Иванов Иван Иванович"
                },
                {
                    "id": "tab_num",
                    "type": "text",
                    "label": "Табельный номер",
                    "required": True,
                    "placeholder": "123456"
                },
                {
                    "id": "direction",
                    "type": "select",
                    "label": "Направление",
                    "required": True,
                    "placeholder": "Выберите направление",
                    "options": [
                        {"value": "Санкт-Петербург", "label": "Санкт-Петербург"},
                        {"value": "Новосибирск", "label": "Новосибирск"},
                        {"value": "Екатеринбург", "label": "Екатеринбург"},
                        {"value": "Казань", "label": "Казань"},
                        {"value": "Сочи", "label": "Сочи"}
                    ]
                },
                {
                    "id": "wishes",
                    "type": "textarea",
                    "label": "Пожелания к рейсу",
                    "required": False,
                    "placeholder": "Укажите особые пожелания или требования..."
                }
            ],
            "submit_button": {
                "text": "Отправить заявку",
                "color": "#2196f3"
            }
        }
    
    def process_application(self, form_data, user_context):
        """Обработка заявки согласно Express API"""
        try:
            # Подготавливаем данные для отправки в основную систему
            application_data = {
                "user_id": user_context.get('user_id', 'express_user'),
                "user_name": user_context.get('user_name', 'Express User'),
                "location": form_data.get('location'),
                "oke": form_data.get('oke'),
                "date": form_data.get('date'),
                "position": form_data.get('position'),
                "fio": form_data.get('fio'),
                "tab_num": form_data.get('tab_num'),
                "direction": form_data.get('direction'),
                "wishes": form_data.get('wishes', ''),
                "platform": "express_smartapp",
                "submitted_at": datetime.now().isoformat(),
                "express_context": user_context
            }
            
            # Отправляем в основную систему
            response = requests.post(
                f"{self.api_url}/api/application",
                json=application_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": "Заявка успешно отправлена!",
                    "application_id": result.get('application_id'),
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "message": f"Ошибка отправки заявки: {response.status_code}",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"Ошибка обработки заявки: {e}")
            return {
                "success": False,
                "message": "Ошибка соединения с сервером",
                "error": str(e)
            }
    
    def get_user_applications(self, user_id):
        """Получение заявок пользователя"""
        try:
            response = requests.get(
                f"{self.api_url}/api/applications/user/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "applications": data.get('applications', []),
                    "total": data.get('total', 0)
                }
            else:
                return {
                    "success": False,
                    "applications": [],
                    "error": f"Ошибка получения заявок: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения заявок: {e}")
            return {
                "success": False,
                "applications": [],
                "error": "Ошибка соединения с сервером"
            }
    
    def get_application_periods(self):
        """Получение активных периодов подачи заявок"""
        try:
            response = requests.get(
                f"{self.api_url}/api/public/application-periods",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "periods": data.get('periods', []),
                    "total": data.get('total', 0)
                }
            else:
                return {
                    "success": False,
                    "periods": [],
                    "error": f"Ошибка получения периодов: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения периодов: {e}")
            return {
                "success": False,
                "periods": [],
                "error": "Ошибка соединения с сервером"
            }
    
    def get_statistics(self):
        """Получение статистики по заявкам"""
        try:
            response = requests.get(
                f"{self.api_url}/api/statistics",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "statistics": data.get('statistics', {}),
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "statistics": {},
                    "error": f"Ошибка получения статистики: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {
                "success": False,
                "statistics": {},
                "error": "Ошибка соединения с сервером"
            }

# Создаем экземпляр SmartApp
smartapp = ExpressSmartApp()

# Express SmartApp API эндпоинты
@app.route('/manifest', methods=['GET'])
def get_manifest():
    """Манифест SmartApp для Express"""
    return jsonify(smartapp.get_manifest())

@app.route('/interface', methods=['GET'])
def get_main_interface():
    """Главный интерфейс SmartApp"""
    return jsonify(smartapp.get_main_interface())

@app.route('/form', methods=['GET'])
def get_application_form():
    """Конфигурация формы подачи заявки"""
    return jsonify(smartapp.get_application_form_config())

@app.route('/submit', methods=['POST'])
def submit_application():
    """Отправка заявки"""
    try:
        data = request.get_json()
        form_data = data.get('form_data', {})
        user_context = data.get('user_context', {})
        
        result = smartapp.process_application(form_data, user_context)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Ошибка обработки заявки: {e}")
        return jsonify({
            "success": False,
            "message": "Ошибка обработки заявки",
            "error": str(e)
        }), 500

@app.route('/applications/<user_id>', methods=['GET'])
def get_user_applications(user_id):
    """Получение заявок пользователя"""
    result = smartapp.get_user_applications(user_id)
    return jsonify(result)

@app.route('/periods', methods=['GET'])
def get_application_periods():
    """Получение периодов подачи заявок"""
    result = smartapp.get_application_periods()
    return jsonify(result)

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Получение статистики"""
    result = smartapp.get_statistics()
    return jsonify(result)

# Webhook для Express
@app.route('/webhook', methods=['POST'])
def express_webhook():
    """Webhook для получения событий от Express"""
    try:
        data = request.get_json()
        event_type = data.get('type')
        user_id = data.get('user_id')
        
        logger.info(f"Получено событие от Express: {event_type} для пользователя {user_id}")
        
        # Обработка различных типов событий
        if event_type == 'user_joined':
            return jsonify({"status": "ok", "message": "Пользователь добавлен"})
        elif event_type == 'user_left':
            return jsonify({"status": "ok", "message": "Пользователь удален"})
        elif event_type == 'message_received':
            return jsonify({"status": "ok", "message": "Сообщение получено"})
        else:
            return jsonify({"status": "ok", "message": "Событие обработано"})
            
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Дополнительный webhook endpoint для совместимости с манифестом
@app.route('/webhook/smartapp', methods=['POST'])
def express_webhook_smartapp():
    """Webhook для SmartApp (совместимость с манифестом)"""
    return express_webhook()

# HTML интерфейс для Express SmartApp
@app.route('/', methods=['GET'])
def smartapp_interface():
    """HTML интерфейс SmartApp для Express"""
    html_template = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Express SmartApp - Заявки на рейсы</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 18px;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .menu-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 24px;
                margin-bottom: 40px;
            }
            
            .menu-item {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .menu-item::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .menu-item:hover::before {
                left: 100%;
            }
            
            .menu-item:hover {
                background: #e3f2fd;
                border-color: #2196f3;
                transform: translateY(-4px);
                box-shadow: 0 8px 25px rgba(33, 150, 243, 0.15);
            }
            
            .menu-item h3 {
                font-size: 20px;
                color: #333;
                margin-bottom: 12px;
                font-weight: 600;
            }
            
            .menu-item p {
                color: #666;
                font-size: 14px;
                line-height: 1.5;
            }
            
            .form-container {
                display: none;
                background: #f8f9fa;
                border-radius: 16px;
                padding: 32px;
                margin-top: 24px;
            }
            
            .form-container h3 {
                color: #333;
                margin-bottom: 24px;
                font-size: 24px;
            }
            
            .form-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
                font-size: 14px;
            }
            
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 14px 16px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: white;
            }
            
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #2196f3;
                box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }
            
            .result {
                margin-top: 24px;
                padding: 20px;
                border-radius: 10px;
                display: none;
                font-weight: 500;
            }
            
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #2196f3;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✈️ Express SmartApp</h1>
                <p>Система подачи заявок на командировочные рейсы</p>
            </div>
            <div class="content">
                <div class="menu-grid">
                    <div class="menu-item" onclick="showForm()">
                        <h3>📝 Подать заявку</h3>
                        <p>Создать новую заявку на рейс</p>
                    </div>
                    <div class="menu-item" onclick="showApplications()">
                        <h3>📋 Мои заявки</h3>
                        <p>Просмотр моих заявок</p>
                    </div>
                    <div class="menu-item" onclick="showPeriods()">
                        <h3>📅 Периоды подачи</h3>
                        <p>Активные периоды подачи заявок</p>
                    </div>
                    <div class="menu-item" onclick="showStatistics()">
                        <h3>📊 Статистика</h3>
                        <p>Статистика по заявкам</p>
                    </div>
                </div>
                
                <div id="formContainer" class="form-container">
                    <h3>Подача заявки на рейс</h3>
                    <form id="applicationForm">
                        <div class="form-grid">
                            <div class="form-group">
                                <label for="location">Локация:</label>
                                <select id="location" required>
                                    <option value="">Выберите локацию</option>
                                    <option value="Москва">Москва</option>
                                    <option value="Санкт-Петербург">Санкт-Петербург</option>
                                    <option value="Новосибирск">Новосибирск</option>
                                    <option value="Екатеринбург">Екатеринбург</option>
                                    <option value="Красноярск">Красноярск</option>
                                    <option value="Сочи">Сочи</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="oke">ОКЭ:</label>
                                <select id="oke" required>
                                    <option value="">Выберите ОКЭ</option>
                                    <option value="ОКЭ 1">ОКЭ 1</option>
                                    <option value="ОКЭ 2">ОКЭ 2</option>
                                    <option value="ОКЭ 3">ОКЭ 3</option>
                                    <option value="ОКЭ 4">ОКЭ 4</option>
                                    <option value="ОКЭ 5">ОКЭ 5</option>
                                    <option value="ОКЭ Красноярск">ОКЭ Красноярск</option>
                                    <option value="ОКЭ Сочи">ОКЭ Сочи</option>
                                    <option value="ОЛСиТ">ОЛСиТ</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="date">Дата вылета:</label>
                                <input type="date" id="date" required>
                            </div>
                            <div class="form-group">
                                <label for="position">Должность:</label>
                                <select id="position" required>
                                    <option value="">Выберите должность</option>
                                    <option value="БП">БП</option>
                                    <option value="РП">РП</option>
                                    <option value="Специалист">Специалист</option>
                                    <option value="Эксперт">Эксперт</option>
                                    <option value="Руководитель">Руководитель</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="fio">ФИО:</label>
                                <input type="text" id="fio" placeholder="Иванов Иван Иванович" required>
                            </div>
                            <div class="form-group">
                                <label for="tab_num">Табельный номер:</label>
                                <input type="text" id="tab_num" placeholder="123456" required>
                            </div>
                            <div class="form-group">
                                <label for="direction">Направление:</label>
                                <select id="direction" required>
                                    <option value="">Выберите направление</option>
                                    <option value="Санкт-Петербург">Санкт-Петербург</option>
                                    <option value="Новосибирск">Новосибирск</option>
                                    <option value="Екатеринбург">Екатеринбург</option>
                                    <option value="Казань">Казань</option>
                                    <option value="Сочи">Сочи</option>
                                </select>
                            </div>
                            <div class="form-group" style="grid-column: 1 / -1;">
                                <label for="wishes">Пожелания к рейсу:</label>
                                <textarea id="wishes" placeholder="Укажите особые пожелания или требования..." rows="3"></textarea>
                            </div>
                        </div>
                        <button type="submit" class="btn">Отправить заявку</button>
                    </form>
                    <div id="loading" class="loading">
                        <div class="spinner"></div>
                        <p>Отправка заявки...</p>
                    </div>
                    <div id="result" class="result"></div>
                </div>
            </div>
        </div>

        <script>
            function showForm() {
                document.getElementById('formContainer').style.display = 'block';
            }
            
            function showApplications() {
                alert('Функция "Мои заявки" в разработке');
            }
            
            function showPeriods() {
                alert('Функция "Периоды подачи" в разработке');
            }
            
            function showStatistics() {
                alert('Функция "Статистика" в разработке');
            }
            
            document.getElementById('applicationForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = {
                    location: document.getElementById('location').value,
                    oke: document.getElementById('oke').value,
                    date: document.getElementById('date').value,
                    position: document.getElementById('position').value,
                    fio: document.getElementById('fio').value,
                    tab_num: document.getElementById('tab_num').value,
                    direction: document.getElementById('direction').value,
                    wishes: document.getElementById('wishes').value
                };
                
                const userContext = {
                    user_id: 'express_user_' + Date.now(),
                    user_name: 'Express User',
                    platform: 'express_smartapp'
                };
                
                // Показываем загрузку
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    const response = await fetch('/submit', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            form_data: formData,
                            user_context: userContext
                        })
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('result');
                    
                    // Скрываем загрузку
                    document.getElementById('loading').style.display = 'none';
                    
                    if (result.success) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <strong>✅ ${result.message}</strong><br>
                            <small>ID заявки: ${result.application_id || 'N/A'}</small>
                        `;
                        resultDiv.style.display = 'block';
                        document.getElementById('applicationForm').reset();
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `
                            <strong>❌ ${result.message}</strong><br>
                            <small>${result.error || ''}</small>
                        `;
                        resultDiv.style.display = 'block';
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    const resultDiv = document.getElementById('result');
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <strong>❌ Ошибка отправки заявки</strong><br>
                        <small>${error.message}</small>
                    `;
                    resultDiv.style.display = 'block';
                }
            });
            
            // Установка минимальной даты
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('date').min = today;
        </script>
    </body>
    </html>
    """
    return html_template

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья SmartApp"""
    return jsonify({
        "status": "ok",
        "app_name": EXPRESS_SMARTAPP_CONFIG['app_name'],
        "version": EXPRESS_SMARTAPP_CONFIG['app_version'],
        "timestamp": datetime.now().isoformat(),
        "express_integration": True
    })

if __name__ == '__main__':
    logger.info(f"🚀 Запуск Express SmartApp: {EXPRESS_SMARTAPP_CONFIG['app_name']} v{EXPRESS_SMARTAPP_CONFIG['app_version']}")
    logger.info(f"📱 SmartApp доступен по адресу: http://localhost:5005/")
    logger.info(f"🔗 API URL: {EXPRESS_SMARTAPP_CONFIG['api_base_url']}")
    logger.info(f"📋 Манифест: http://localhost:5005/manifest")
    
    app.run(host='0.0.0.0', port=5005, debug=True)






