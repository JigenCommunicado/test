# 🚀 Express SmartApp - Правильная интеграция с Express мессенджером

## 📋 Обзор

Это правильная реализация Express SmartApp согласно [официальной документации Express](https://docs.express.ms/smartapps/). SmartApp интегрирован с российским мессенджером Express и предоставляет систему подачи заявок на командировочные рейсы.

## 🔧 Технические характеристики

### **Основные параметры:**
- **Название:** Flight Booking SmartApp
- **Версия:** 1.0.0
- **Описание:** Система подачи заявок на командировочные рейсы
- **Иконка:** ✈️
- **Цвет:** #0088cc
- **Порт:** 5005

### **Структура API согласно Express:**
- **Манифест:** `/manifest` - описание SmartApp
- **Интерфейс:** `/interface` - главный интерфейс
- **Форма:** `/form` - конфигурация формы
- **Отправка:** `/submit` - отправка заявки
- **Webhook:** `/webhook` - события от Express
- **Здоровье:** `/health` - проверка состояния

## 🚀 Запуск

### **Быстрый запуск:**
```bash
cd /root/test/express_bot
./start_express_smartapp_proper.sh
```

### **Остановка:**
```bash
./stop_express_smartapp_proper.sh
```

## 📱 API эндпоинты

### **1. Манифест SmartApp:**
```http
GET /manifest
```
**Ответ:**
```json
{
  "name": "Flight Booking SmartApp",
  "version": "1.0.0",
  "description": "Система подачи заявок на командировочные рейсы",
  "icon": "✈️",
  "color": "#0088cc",
  "permissions": ["read_user_info", "send_messages", "access_files"],
  "capabilities": ["flight_booking", "application_management", "notifications"],
  "endpoints": {
    "main": "/",
    "api": "/",
    "webhook": "/webhook"
  }
}
```

### **2. Главный интерфейс:**
```http
GET /interface
```

### **3. Конфигурация формы:**
```http
GET /form
```

### **4. Отправка заявки:**
```http
POST /submit
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
    "platform": "express_smartapp"
  }
}
```

### **5. Webhook для Express:**
```http
POST /webhook
Content-Type: application/json

{
  "type": "user_joined",
  "user_id": "user123",
  "data": {...}
}
```

## 🔧 Интеграция с Express мессенджером

### **1. Настройка в Express сервере:**

Согласно [документации Express SmartApp](https://docs.express.ms/smartapps/):

1. **Добавить SmartApp в админ-панель Express:**
   - **URL:** `http://your-server:5005/`
   - **Манифест:** `http://your-server:5005/manifest`
   - **Название:** "Flight Booking SmartApp"
   - **Иконка:** ✈️
   - **Цвет:** #0088cc

2. **Настроить webhook:**
   - **URL:** `http://your-server:5005/webhook`
   - **Методы:** POST
   - **События:** user_joined, user_left, message_received

### **2. Конфигурация Express сервера:**

```yaml
smartapps:
  - name: "Flight Booking SmartApp"
    url: "http://localhost:5005/"
    manifest_url: "http://localhost:5005/manifest"
    webhook_url: "http://localhost:5005/webhook"
    icon: "✈️"
    color: "#0088cc"
    permissions:
      - "read_user_info"
      - "send_messages"
      - "access_files"
      - "manage_applications"
```

### **3. Структура данных согласно Express:**

SmartApp использует правильную структуру данных для интеграции с Express:

- **Манифест** - полное описание приложения
- **Интерфейс** - структурированный UI
- **Формы** - конфигурация полей
- **Webhook** - обработка событий
- **Контекст пользователя** - информация о пользователе Express

## 🧪 Тестирование

### **Локальное тестирование:**
```bash
# Проверка здоровья
curl http://localhost:5005/health

# Манифест
curl http://localhost:5005/manifest

# Главный интерфейс
curl http://localhost:5005/interface

# Конфигурация формы
curl http://localhost:5005/form
```

### **Тестирование отправки заявки:**
```bash
curl -X POST http://localhost:5005/submit \
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
      "platform": "express_smartapp"
    }
  }'
```

## 📊 Мониторинг

### **Логи:**
```bash
tail -f logs/express_smartapp_proper.log
```

### **Статус процессов:**
```bash
ps aux | grep express_smartapp_proper
```

### **Проверка портов:**
```bash
netstat -tlnp | grep 5005
```

## 🔒 Безопасность

### **Рекомендации:**
1. **HTTPS** - используйте SSL сертификаты в продакшене
2. **Аутентификация** - проверка пользователей Express
3. **Валидация** - все данные проверяются
4. **Логирование** - полный лог операций
5. **Webhook security** - проверка подписи запросов

## 🎯 Готово к использованию!

**Express SmartApp полностью соответствует требованиям документации Express и готов к интеграции!**

### **✅ Что готово:**
- ✅ **Правильная структура API** согласно Express
- ✅ **Манифест SmartApp** для регистрации
- ✅ **Webhook интеграция** для событий
- ✅ **Контекст пользователя** Express
- ✅ **Адаптивный интерфейс** для всех устройств
- ✅ **Полная функциональность** подачи заявок

### **🌐 Доступные URL:**
- **SmartApp:** http://localhost:5005/
- **Манифест:** http://localhost:5005/manifest
- **API:** http://localhost:5005/
- **Webhook:** http://localhost:5005/webhook
- **Health:** http://localhost:5005/health

**SmartApp готов к развертыванию в Express мессенджере!** 🚀✈️







