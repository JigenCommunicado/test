# Настройка IDE для Express Bot

## Проблема
IDE (VS Code/Cursor) не видит виртуальное окружение и показывает ошибки импорта.

## Решение

### 1. Перезапустите IDE
После создания конфигурационных файлов перезапустите VS Code/Cursor.

### 2. Выберите правильный интерпретатор Python
1. Откройте Command Palette (`Ctrl+Shift+P`)
2. Выберите "Python: Select Interpreter"
3. Выберите: `/root/test/express_bot/venv/bin/python3`

### 3. Альтернативный способ - через статус бар
1. Внизу экрана найдите версию Python в статус баре
2. Нажмите на неё
3. Выберите правильный интерпретатор

### 4. Проверка настройки
После выбора интерпретатора:
1. Откройте `admin_server.py`
2. Ошибки импорта должны исчезнуть
3. В статус баре должно быть: `Python 3.12.x ('venv': venv)`

## Файлы конфигурации

Созданы следующие файлы:
- `.vscode/settings.json` - настройки VS Code
- `.vscode/launch.json` - конфигурация запуска
- `pyrightconfig.json` - конфигурация Pyright
- `.python-version` - версия Python

## Если проблема не решается

1. Убедитесь, что виртуальное окружение создано:
   ```bash
   cd /root/test/express_bot
   ls -la venv/bin/python3
   ```

2. Убедитесь, что пакеты установлены:
   ```bash
   cd /root/test/express_bot
   source venv/bin/activate
   pip list | grep -E "(flask|psutil|openpyxl)"
   ```

3. Перезагрузите окно VS Code:
   - `Ctrl+Shift+P` → "Developer: Reload Window"

## Запуск сервера

После настройки IDE сервер можно запускать:
```bash
cd /root/test/express_bot
./admin_server.py
```

Или через VS Code:
- `F5` (используя конфигурацию "Admin Server")


