#!/usr/bin/env python3
"""
Тестовый SmartApp для проверки Excel интеграции
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from excel_integration import ExcelIntegration

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Разрешить CORS для всех доменов

# Инициализация Excel интеграции
excel_integration = ExcelIntegration(data_dir="data")

# Хранение данных пользователей (в памяти для тестирования)
user_data = {}

class UserData:
    def __init__(self):
        self.location = None
        self.oke = None
        self.selected_date = None
        self.position = None
        self.fio = None
        self.tab_num = None
        self.direction = None
        self.flight_wishes = None

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = UserData()
    return user_data[user_id]

@app.route('/')
def index():
    """Главная страница тестового SmartApp"""
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Тестовый SmartApp - Excel интеграция</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .test-section { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }
            .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-info { background: #17a2b8; color: white; }
            .result { margin-top: 15px; padding: 10px; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Тестовый SmartApp - Excel интеграция</h1>
            
            <div class="test-section">
                <h3>📊 Тест Excel интеграции</h3>
                <button class="btn btn-primary" onclick="testExcelIntegration()">Проверить Excel интеграцию</button>
                <button class="btn btn-info" onclick="getStatistics()">Получить статистику</button>
                <div id="excel-result"></div>
            </div>

            <div class="test-section">
                <h3>📝 Создать тестовую заявку</h3>
                <button class="btn btn-success" onclick="createTestApplication()">Создать тестовую заявку</button>
                <div id="application-result"></div>
            </div>

            <div class="test-section">
                <h3>🔧 API тесты</h3>
                <button class="btn btn-primary" onclick="testAPI()">Тест всех API</button>
                <div id="api-result"></div>
            </div>
        </div>

        <script>
            function showResult(elementId, message, type = 'info') {
                const element = document.getElementById(elementId);
                element.innerHTML = `<div class="result ${type}">${message}</div>`;
            }

            async function testExcelIntegration() {
                try {
                    const response = await fetch('/api/statistics');
                    const data = await response.json();
                    
                    if (response.ok) {
                        showResult('excel-result', `✅ Excel интеграция работает!<br><pre>${JSON.stringify(data, null, 2)}</pre>`, 'success');
                    } else {
                        showResult('excel-result', `❌ Ошибка: ${data.error}`, 'error');
                    }
                } catch (error) {
                    showResult('excel-result', `❌ Ошибка: ${error.message}`, 'error');
                }
            }

            async function getStatistics() {
                try {
                    const response = await fetch('/api/statistics');
                    const data = await response.json();
                    
                    if (response.ok) {
                        const stats = data.statistics;
                        let statsText = 'Статистика заявок:\\n';
                        for (const [oke, count] of Object.entries(stats)) {
                            statsText += `${oke}: ${count} заявок\\n`;
                        }
                        showResult('excel-result', `📊 Статистика получена:<br><pre>${statsText}</pre>`, 'info');
                    } else {
                        showResult('excel-result', `❌ Ошибка: ${data.error}`, 'error');
                    }
                } catch (error) {
                    showResult('excel-result', `❌ Ошибка: ${error.message}`, 'error');
                }
            }

            async function createTestApplication() {
                const userId = 'test_' + Date.now();
                
                try {
                    // Создаем тестовую заявку
                    const steps = [
                        { endpoint: '/api/start', data: { user_id: userId } },
                        { endpoint: '/api/select-location', data: { user_id: userId, location: 'МСК' } },
                        { endpoint: '/api/select-oke', data: { user_id: userId, oke: 'ОКЭ 1' } },
                        { endpoint: '/api/select-date', data: { user_id: userId, date: '20.09.2024' } },
                        { endpoint: '/api/select-position', data: { user_id: userId, position: 'БП' } },
                        { endpoint: '/api/input-fio', data: { user_id: userId, fio: 'Тест Тест Тестович', tab_num: '123456' } },
                        { endpoint: '/api/select-direction', data: { user_id: userId, direction: 'Санкт-Петербург' } },
                        { endpoint: '/api/input-wishes', data: { user_id: userId, wishes: 'Тестовая заявка' } }
                    ];

                    let result = 'Создание тестовой заявки:\\n';
                    
                    for (let i = 0; i < steps.length; i++) {
                        const step = steps[i];
                        const response = await fetch(step.endpoint, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(step.data)
                        });
                        
                        if (!response.ok) {
                            const errorData = await response.json();
                            throw new Error(`Шаг ${i + 1}: ${errorData.error}`);
                        }
                        
                        result += `✅ Шаг ${i + 1}: ${step.endpoint}\\n`;
                    }

                    // Подтверждаем заявку
                    const response = await fetch('/api/confirm', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId })
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(`Подтверждение: ${errorData.error}`);
                    }
                    
                    result += '✅ Заявка подтверждена и сохранена в Excel!';
                    showResult('application-result', `<pre>${result}</pre>`, 'success');
                    
                } catch (error) {
                    showResult('application-result', `❌ Ошибка: ${error.message}`, 'error');
                }
            }

            async function testAPI() {
                const endpoints = [
                    { name: 'Health', url: '/api/health', method: 'GET' },
                    { name: 'Statistics', url: '/api/statistics', method: 'GET' }
                ];

                let result = 'Тест API endpoints:\\n';
                
                for (const endpoint of endpoints) {
                    try {
                        const response = await fetch(endpoint.url, { method: endpoint.method });
                        if (response.ok) {
                            result += `✅ ${endpoint.name}: OK (${response.status})\\n`;
                        } else {
                            result += `❌ ${endpoint.name}: Failed (${response.status})\\n`;
                        }
                    } catch (error) {
                        result += `❌ ${endpoint.name}: Error - ${error.message}\\n`;
                    }
                }
                
                showResult('api-result', `<pre>${result}</pre>`, 'info');
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/health')
def api_health():
    """API для проверки состояния"""
    return jsonify({
        'success': True,
        'app_name': 'Тестовый SmartApp',
        'version': '1.0.0',
        'excel_integration': 'active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/statistics')
def api_statistics():
    """API для получения статистики заявок"""
    try:
        stats = excel_integration.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    """API для начала заявки"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        
        user_data_obj = get_user_data(user_id)
        # Сбрасываем данные пользователя
        
        return jsonify({
            'success': True,
            'message': 'Заявка начата',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Ошибка в api_start: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/select-location', methods=['POST'])
def api_select_location():
    """API для выбора локации"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        location = data.get('location')
        
        if not location or location.strip() == '':
            return jsonify({'success': False, 'error': 'Локация не указана'}), 400
        
        user_data_obj = get_user_data(user_id)
        user_data_obj.location = location
        
        return jsonify({
            'success': True,
            'message': f'Локация {location} выбрана'
        })
    except Exception as e:
        logger.error(f"Ошибка в api_select_location: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/select-oke', methods=['POST'])
def api_select_oke():
    """API для выбора ОКЭ"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        oke = data.get('oke')
        
        user_data_obj = get_user_data(user_id)
        user_data_obj.oke = oke
        
        return jsonify({
            'success': True,
            'message': f'ОКЭ {oke} выбрано'
        })
    except Exception as e:
        logger.error(f"Ошибка в api_select_oke: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/select-date', methods=['POST'])
def api_select_date():
    """API для выбора даты"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        date = data.get('date')
        
        user_data_obj = get_user_data(user_id)
        user_data_obj.selected_date = date
        
        return jsonify({
            'success': True,
            'message': f'Дата {date} выбрана'
        })
    except Exception as e:
        logger.error(f"Ошибка в api_select_date: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/select-position', methods=['POST'])
def api_select_position():
    """API для выбора должности"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        position = data.get('position')
        
        user_data_obj = get_user_data(user_id)
        user_data_obj.position = position
        
        return jsonify({
            'success': True,
            'message': f'Должность {position} выбрана'
        })
    except Exception as e:
        logger.error(f"Ошибка в api_select_position: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/input-fio', methods=['POST'])
def api_input_fio():
    """API для ввода ФИО"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        fio = data.get('fio')
        tab_num = data.get('tab_num')
        
        if not fio or not tab_num or fio.strip() == '' or tab_num.strip() == '':
            return jsonify({'success': False, 'error': 'ФИО и табельный номер обязательны'}), 400
        
        user_data_obj = get_user_data(user_id)
        user_data_obj.fio = fio
        user_data_obj.tab_num = tab_num
        
        return jsonify({
            'success': True,
            'message': f'ФИО {fio} введено'
        })
    except Exception as e:
        logger.error(f"Ошибка в api_input_fio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/select-direction', methods=['POST'])
def api_select_direction():
    """API для выбора направления"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        direction = data.get('direction')
        
        user_data_obj = get_user_data(user_id)
        user_data_obj.direction = direction
        
        return jsonify({
            'success': True,
            'message': f'Направление {direction} выбрано'
        })
    except Exception as e:
        logger.error(f"Ошибка в api_select_direction: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/input-wishes', methods=['POST'])
def api_input_wishes():
    """API для ввода пожеланий"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        wishes = data.get('wishes')
        
        user_data_obj = get_user_data(user_id)
        user_data_obj.flight_wishes = wishes
        
        return jsonify({
            'success': True,
            'message': 'Пожелания введены'
        })
    except Exception as e:
        logger.error(f"Ошибка в api_input_wishes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/confirm', methods=['POST'])
def api_confirm():
    """API для подтверждения заявки"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        
        user_data_obj = get_user_data(user_id)
        
        # Проверяем, что все данные собраны
        if not all([user_data_obj.location, user_data_obj.oke, user_data_obj.selected_date,
                   user_data_obj.position, user_data_obj.fio, user_data_obj.tab_num,
                   user_data_obj.direction, user_data_obj.flight_wishes]):
            return jsonify({'success': False, 'error': 'Не все данные собраны'}), 400
        
        # Сохраняем в Excel
        try:
            full_flight_info = f"{user_data_obj.selected_date} {user_data_obj.flight_wishes}"
            
            if not excel_integration.add_application(
                oke=user_data_obj.oke,
                fio=user_data_obj.fio,
                tab_num=user_data_obj.tab_num,
                position=user_data_obj.position,
                direction=user_data_obj.direction,
                flight_info=full_flight_info
            ):
                logger.error(f"❌ Не удалось сохранить заявку в Excel для '{user_data_obj.oke}'")
                return jsonify({'success': False, 'error': f'Не удалось сохранить заявку в Excel'}), 500
            
            logger.info(f"✅ Заявка сохранена в Excel: {user_data_obj.fio} - {user_data_obj.oke}")
            
            return jsonify({
                'success': True,
                'message': 'Заявка успешно отправлена и сохранена в Excel!'
            })
        except Exception as e:
            logger.error(f"Ошибка при записи заявки: {e}")
            return jsonify({'success': False, 'error': f'Ошибка при сохранении: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Ошибка в api_confirm: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Запуск тестового SmartApp...")
    print("📊 Excel интеграция активна")
    print("🌐 URL: http://localhost:8081/")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=8081, debug=False)
