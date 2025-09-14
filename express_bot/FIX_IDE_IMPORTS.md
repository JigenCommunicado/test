# Исправление ошибок импорта в IDE

## Проблема
IDE показывает ошибки импорта для Flask, psutil, openpyxl и других пакетов, хотя они установлены в виртуальном окружении.

## Решение

### Шаг 1: Перезапустите IDE
1. Закройте VS Code/Cursor полностью
2. Откройте заново
3. Откройте папку `/root/test/express_bot`

### Шаг 2: Выберите правильный интерпретатор Python
1. Нажмите `Ctrl+Shift+P`
2. Введите "Python: Select Interpreter"
3. Выберите: `/root/test/express_bot/venv/bin/python3`

### Шаг 3: Альтернативный способ
1. Внизу экрана найдите версию Python в статус баре
2. Нажмите на неё
3. Выберите правильный интерпретатор

### Шаг 4: Проверка
После выбора интерпретатора:
1. Откройте `admin_server.py`
2. Ошибки импорта должны исчезнуть
3. В статус баре должно быть: `Python 3.12.x ('venv': venv)`

## Если проблема не решается

### Вариант 1: Перезагрузите окно
1. `Ctrl+Shift+P`
2. "Developer: Reload Window"

### Вариант 2: Проверьте конфигурацию
Запустите скрипт проверки:
```bash
cd /root/test/express_bot
./venv/bin/python3 check_ide_config.py
```

### Вариант 3: Ручная настройка
1. Откройте Command Palette (`Ctrl+Shift+P`)
2. "Python: Configure Tests"
3. Выберите pytest или unittest
4. Выберите правильный интерпретатор

## Файлы конфигурации

Созданы следующие файлы:
- `pyrightconfig.json` - конфигурация Pyright/BasedPyright
- `.vscode/settings.json` - настройки VS Code
- `.vscode/launch.json` - конфигурация запуска
- `.vscode/workspace.code-workspace` - настройки workspace
- `check_ide_config.py` - скрипт проверки

## Запуск сервера

После исправления ошибок импорта:

```bash
# Прямой запуск
cd /root/test/express_bot
./admin_server.py

# Или через launcher
python3 run_admin_server.py

# Или через Makefile
make run
```

## Проверка работы

1. Запустите сервер
2. Откройте http://localhost:5006
3. Должна открыться админ панель

## Если ничего не помогает

1. Удалите папку `.vscode`
2. Перезапустите IDE
3. Выберите интерпретатор заново
4. Или используйте командную строку для запуска


