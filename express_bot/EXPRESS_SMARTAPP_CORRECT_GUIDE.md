# 🚀 Express SmartApp - Правильная интеграция согласно документации

## 📋 Обзор

Это **правильная реализация Express SmartApp** согласно [официальному руководству разработчика Express](https://docs.express.ms/smartapps/developer-guide/). SmartApp состоит из двух компонентов: **Frontend (SPA)** и **Backend (Чат-бот)**.

## 🏗️ Архитектура согласно документации Express

### **Frontend (SPA-приложение)**
- **Файл:** `express_smartapp_frontend.html`
- **Выполняется:** во встроенном **WebView/iFrame** клиента Express
- **Тип:** Single Page Application (SPA)
- **Взаимодействие:** с Backend через **Bot API**

### **Backend (Чат-бот)**
- **Файл:** `express_smartapp_bot.py`
- **Реализует:** **Bot API** для получения информации от frontend
- **Работает с:** **BotX API** для интеграции с Express
- **Авторизация:** НЕ содержит элементов авторизации (через Express)
- **Безопасность:** Зашифрованное взаимодействие между frontend и BotX
- **Токены:** Передает токен авторизации в каждом запросе к BotX API

## 🔧 Технические характеристики

### **Основные параметры:**
- **Название:** Flight Booking SmartApp
- **Версия:** 1.0.0
- **Порт:** 5006
- **Frontend:** SPA в WebView Express
- **Backend:** Чат-бот с Bot API

### **API структура:**
- **Frontend:** `http://localhost:5006/` - SPA для WebView
- **Bot API:** `http://localhost:5006/api/smartapp/` - без авторизации
- **Health:** `http://localhost:5006/health` - проверка состояния

## 🚀 Запуск

### **Быстрый запуск:**
```bash
cd /root/test/express_bot
./start_express_smartapp_correct.sh
```

### **Остановка:**
```bash
./stop_express_smartapp_correct.sh
```

## 📱 Frontend (SPA)

### **Особенности:**
- **Адаптивный дизайн** для WebView Express
- **Компактный интерфейс** для мобильных устройств
- **JavaScript класс** `ExpressSmartApp` для управления
- **Взаимодействие** с Backend через Bot API

### **Функциональность:**
- 📝 **Подача заявки** - форма с валидацией
- 📋 **Мои заявки** - просмотр заявок пользователя
- 📅 **Периоды подачи** - активные периоды
- 📊 **Статистика** - статистика по заявкам

## 🤖 Backend (Чат-бот)

### **Bot API эндпоинты (без авторизации):**

#### **1. Информация о боте:**
```http
GET /api/smartapp/info
```

#### **2. Отправка заявки:**
```http
POST /api/smartapp/submit
Content-Type: application/json

{
  "form_data": {
    "location": "Москва",
    "oke": "ОКЭ 1",
    "date": "2025-09-20",
    "position": "БП",
    "fio": "Иванов Иван Иванович",
    "tab_num": "123456",
    "direction": "Санкт-Петербург",
    "wishes": "Особые пожелания"
  },
  "user_context": {
    "user_id": "express_user_123",
    "user_name": "Иван Иванов",
    "platform": "express_smartapp",
    "express_token": "token_from_express"
  }
}
```

#### **3. Заявки пользователя:**
```http
GET /api/smartapp/applications/{user_id}
```

#### **4. Периоды подачи:**
```http
GET /api/smartapp/periods
```

#### **5. Статистика:**
```http
GET /api/smartapp/statistics
```

### **BotX API интеграция:**
- **URL:** `http://localhost:8080/api/botx/`
- **Авторизация:** Bearer токен в каждом запросе
- **Fallback:** Flask API если BotX недоступен

## 🔧 Интеграция с Express мессенджером

### **1. Настройка в Express сервере:**

Согласно [документации Express SmartApp](https://docs.express.ms/smartapps/developer-guide/):

1. **Добавить SmartApp в админ-панель Express:**
   - **Frontend URL:** `http://your-server:5006/`
   - **Название:** "Flight Booking SmartApp"
   - **Тип:** SPA в WebView

2. **Настроить чат-бота:**
   - **Bot API URL:** `http://your-server:5006/api/smartapp/`
   - **BotX API URL:** `http://your-server:8080/api/botx/`
   - **Токен:** Настроить в Express

### **2. Конфигурация Express сервера:**

```yaml
smartapps:
  - name: "Flight Booking SmartApp"
    frontend_url: "http://localhost:5006/"
    bot_api_url: "http://localhost:5006/api/smartapp/"
    botx_api_url: "http://localhost:8080/api/botx/"
    type: "spa_webview"
    bot_token: "your_bot_token_here"
```

### **3. Структура данных согласно Express:**

- **Frontend** - SPA для WebView Express
- **Bot API** - без авторизации, получает данные от frontend
- **BotX API** - с токеном авторизации, интеграция с Express
- **Зашифрованное взаимодействие** между компонентами

## 🧪 Тестирование

### **Локальное тестирование:**
```bash
# Проверка здоровья
curl http://localhost:5006/health

# Frontend SPA
curl http://localhost:5006/

# Bot API info
curl http://localhost:5006/api/smartapp/info

# Тест отправки заявки
curl -X POST http://localhost:5006/api/smartapp/submit \
  -H "Content-Type: application/json" \
  -d '{
    "form_data": {
      "location": "Москва",
      "oke": "ОКЭ 1",
      "date": "2025-09-20",
      "position": "БП",
      "fio": "Тест Тестович",
      "tab_num": "123456",
      "direction": "Санкт-Петербург",
      "wishes": "Тестовая заявка"
    },
    "user_context": {
      "user_id": "express_test_user",
      "user_name": "Тест Тестович",
      "platform": "express_smartapp",
      "express_token": "mock_token"
    }
  }'
```

## 📊 Мониторинг

### **Логи:**
```bash
tail -f logs/express_smartapp_bot.log
```

### **Статус процессов:**
```bash
ps aux | grep express_smartapp_bot
```

### **Проверка портов:**
```bash
netstat -tlnp | grep 5006
```

## 🔒 Безопасность

### **Согласно документации Express:**
1. **Зашифрованное взаимодействие** между frontend и BotX
2. **Токен авторизации** в каждом запросе к BotX API
3. **Bot API без авторизации** - только для frontend
4. **Валидация данных** на всех уровнях
5. **Логирование** всех операций

## 🎯 Готово к использованию!

**Express SmartApp полностью соответствует архитектуре из документации Express!**

### **✅ Что готово:**
- ✅ **Frontend SPA** для WebView Express
- ✅ **Backend чат-бот** с Bot API
- ✅ **BotX API интеграция** с токенами
- ✅ **Зашифрованное взаимодействие**
- ✅ **Правильная архитектура** согласно документации

### **🌐 Доступные URL:**
- **Frontend SPA:** http://localhost:5006/
- **Bot API:** http://localhost:5006/api/smartapp/
- **Health Check:** http://localhost:5006/health

### **🔧 Интеграция с Express:**
1. **Frontend** загружается в WebView Express
2. **Bot API** обрабатывает запросы от frontend
3. **BotX API** интегрируется с Express сервером
4. **Токены авторизации** передаются в каждом запросе

**SmartApp готов к развертыванию в Express мессенджере согласно официальной документации!** 🚀✈️







