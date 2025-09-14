#!/usr/bin/env python3
"""
API Proxy для Telegram Mini App
Проксирует запросы от HTTPS Mini App к HTTP Flask API
"""

from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['*'])  # Разрешаем все домены для прокси

# URL внутреннего Flask API
INTERNAL_API_URL = "http://localhost:5002"

@app.route('/proxy/api/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_api(endpoint):
    """Проксирование запросов к внутреннему API"""
    try:
        # Формируем полный URL для внутреннего API
        target_url = f"{INTERNAL_API_URL}/api/{endpoint}"
        
        # Копируем заголовки, исключая некоторые
        headers = {}
        for key, value in request.headers:
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        # Копируем данные запроса
        data = None
        if request.method in ['POST', 'PUT'] and request.is_json:
            data = json.dumps(request.get_json())
            headers['Content-Type'] = 'application/json'
        
        # Отправляем запрос к внутреннему API
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.args,
            timeout=30
        )
        
        # Возвращаем ответ
        return response.content, response.status_code, {
            'Content-Type': response.headers.get('Content-Type', 'application/json'),
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка соединения с API: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка прокси: {str(e)}'
        }), 500

@app.route('/proxy/health')
def proxy_health():
    """Проверка здоровья прокси"""
    try:
        response = requests.get(f"{INTERNAL_API_URL}/health", timeout=5)
        return {
            'proxy_status': 'ok',
            'internal_api_status': 'ok' if response.status_code == 200 else 'error',
            'internal_response': response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            'proxy_status': 'ok',
            'internal_api_status': 'error',
            'error': str(e)
        }, 500

if __name__ == '__main__':
    print("🔗 Запуск API Proxy для Telegram Mini App...")
    print("🎯 Прокси: http://localhost:8445")
    print("🔗 Внутренний API: http://localhost:5002")
    print("📱 Использование: /proxy/api/application вместо /api/application")
    
    app.run(
        host='0.0.0.0',
        port=8445,
        debug=False
    )
