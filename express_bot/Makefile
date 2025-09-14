# Makefile для Express Bot Admin Server

.PHONY: help install run stop test clean

# Переменные
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
ADMIN_SERVER = admin_server.py

help: ## Показать справку
	@echo "Доступные команды:"
	@echo "  make install  - Установить зависимости"
	@echo "  make run      - Запустить admin server"
	@echo "  make stop     - Остановить admin server"
	@echo "  make test     - Проверить установку"
	@echo "  make clean    - Очистить виртуальное окружение"

install: ## Установить зависимости
	@echo "📦 Создание виртуального окружения..."
	python3 -m venv $(VENV)
	@echo "📦 Установка зависимостей..."
	$(PIP) install flask flask-cors psutil openpyxl
	@echo "✅ Установка завершена!"

run: ## Запустить admin server
	@echo "🚀 Запуск Admin Panel Server..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Виртуальное окружение не найдено! Запустите: make install"; \
		exit 1; \
	fi
	$(PYTHON) $(ADMIN_SERVER)

test: ## Проверить установку
	@echo "🔍 Проверка зависимостей..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Виртуальное окружение не найдено!"; \
		exit 1; \
	fi
	$(PYTHON) -c "import flask, flask_cors, psutil, openpyxl; print('✅ Все зависимости установлены')"

stop: ## Остановить admin server
	@echo "🛑 Поиск процессов admin_server.py..."
	@pkill -f admin_server.py || echo "Процессы не найдены"

clean: ## Очистить виртуальное окружение
	@echo "🧹 Удаление виртуального окружения..."
	rm -rf $(VENV)
	@echo "✅ Очистка завершена!"


