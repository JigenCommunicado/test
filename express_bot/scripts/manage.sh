#!/bin/bash

# Главный скрипт управления Express SmartApp
# Автор: AI Assistant
# Дата: $(date)

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для вывода заголовка
print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    Express SmartApp Manager                 ║${NC}"
    echo -e "${CYAN}║                Управление серверами приложения              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Функция для вывода меню
print_menu() {
    echo -e "${YELLOW}Выберите действие:${NC}"
    echo ""
    echo -e "${GREEN}1.${NC} 🚀 Запустить все серверы"
    echo -e "${GREEN}2.${NC} 🛑 Остановить все серверы"
    echo -e "${GREEN}3.${NC} 🔄 Перезапустить все серверы"
    echo -e "${GREEN}4.${NC} 🔍 Проверить статус серверов"
    echo -e "${GREEN}5.${NC} 📝 Показать логи Flask сервера"
    echo -e "${GREEN}6.${NC} 📝 Показать логи статического сервера"
    echo -e "${GREEN}7.${NC} 🌐 Открыть главную страницу в браузере"
    echo -e "${GREEN}8.${NC} 🔧 Открыть админ панель в браузере"
    echo -e "${GREEN}9.${NC} 📊 Показать статистику приложения"
    echo -e "${GREEN}0.${NC} 🚪 Выход"
    echo ""
}

# Функция для показа статистики
show_stats() {
    echo -e "${BLUE}📊 Статистика Express SmartApp:${NC}"
    echo ""
    
    # Проверяем Flask сервер
    if curl -s http://localhost:5002/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Flask API сервер: Запущен${NC}"
        
        # Получаем статистику
        echo -e "${YELLOW}📈 Статистика заявок:${NC}"
        curl -s http://localhost:5002/api/statistics | python3 -m json.tool 2>/dev/null || echo "   ❌ Не удалось получить статистику"
    else
        echo -e "${RED}❌ Flask API сервер: Не запущен${NC}"
    fi
    
    echo ""
    
    # Проверяем статический сервер
    if curl -s http://localhost:8080/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Статический сервер: Запущен${NC}"
    else
        echo -e "${RED}❌ Статический сервер: Не запущен${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}📁 Файлы данных:${NC}"
    if [ -f "data/все_заявки.xlsx" ]; then
        echo -e "   ✅ Excel файл с заявками: $(ls -lh data/все_заявки.xlsx | awk '{print $5}')"
    else
        echo -e "   ❌ Excel файл с заявками: Не найден"
    fi
    
    if [ -f "smartapp.log" ]; then
        echo -e "   ✅ Лог Flask сервера: $(ls -lh smartapp.log | awk '{print $5}')"
    fi
    
    if [ -f "static.log" ]; then
        echo -e "   ✅ Лог статического сервера: $(ls -lh static.log | awk '{print $5}')"
    fi
}

# Функция для показа логов
show_logs() {
    local log_type=$1
    echo -e "${BLUE}📝 Логи $log_type:${NC}"
    echo ""
    
    if [ "$log_type" = "Flask" ]; then
        if [ -f "smartapp.log" ]; then
            tail -20 smartapp.log
        else
            echo -e "${RED}❌ Лог файл Flask сервера не найден${NC}"
        fi
    else
        if [ -f "static.log" ]; then
            tail -20 static.log
        else
            echo -e "${RED}❌ Лог файл статического сервера не найден${NC}"
        fi
    fi
}

# Функция для открытия в браузере
open_browser() {
    local url=$1
    echo -e "${BLUE}🌐 Открытие $url в браузере...${NC}"
    
    # Пытаемся открыть в различных браузерах
    if command -v xdg-open > /dev/null; then
        xdg-open "$url" 2>/dev/null &
    elif command -v firefox > /dev/null; then
        firefox "$url" 2>/dev/null &
    elif command -v google-chrome > /dev/null; then
        google-chrome "$url" 2>/dev/null &
    else
        echo -e "${YELLOW}⚠️  Не удалось открыть браузер автоматически${NC}"
        echo -e "${YELLOW}   Откройте вручную: $url${NC}"
    fi
}

# Основной цикл
main() {
    print_header
    
    while true; do
        print_menu
        read -p "Введите номер действия (0-9): " choice
        
        case $choice in
            1)
                echo -e "${GREEN}🚀 Запуск всех серверов...${NC}"
                ./start_servers.sh
                ;;
            2)
                echo -e "${RED}🛑 Остановка всех серверов...${NC}"
                ./stop_servers.sh
                ;;
            3)
                echo -e "${YELLOW}🔄 Перезапуск всех серверов...${NC}"
                ./restart_servers.sh
                ;;
            4)
                ./status_servers.sh
                ;;
            5)
                show_logs "Flask"
                ;;
            6)
                show_logs "статического сервера"
                ;;
            7)
                open_browser "http://localhost:8080/index.html"
                ;;
            8)
                open_browser "http://localhost:8080/admin_panel.html"
                ;;
            9)
                show_stats
                ;;
            0)
                echo -e "${PURPLE}👋 До свидания!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Неверный выбор. Попробуйте снова.${NC}"
                ;;
        esac
        
        echo ""
        read -p "Нажмите Enter для продолжения..."
        clear
        print_header
    done
}

# Запуск главной функции
main

