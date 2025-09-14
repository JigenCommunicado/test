#!/bin/bash

echo "🔥 Настройка Firewall для Express.ms Bot"
echo "======================================="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo $0"
    exit 1
fi

# Проверка ufw
if ! command -v ufw &> /dev/null; then
    echo "📦 Установка ufw..."
    apt update
    apt install -y ufw
    echo "✅ ufw установлен"
fi

echo "🔧 Настройка правил firewall..."

# Сброс правил
ufw --force reset

# Политика по умолчанию
ufw default deny incoming
ufw default allow outgoing

# SSH (порт 22)
echo "🔑 Разрешение SSH (порт 22)..."
ufw allow 22/tcp comment 'SSH'

# HTTP (порт 80)
echo "🌐 Разрешение HTTP (порт 80)..."
ufw allow 80/tcp comment 'HTTP'

# HTTPS (порт 443)
echo "🔐 Разрешение HTTPS (порт 443)..."
ufw allow 443/tcp comment 'HTTPS'

# Закрытие внутренних портов
echo "🔒 Закрытие внутренних портов..."
ufw deny 5432/tcp comment 'PostgreSQL (внутренний)'
ufw deny 6379/tcp comment 'Redis (внутренний)'
ufw deny 8000/tcp comment 'Bot Server (внутренний)'

# Дополнительные порты для мониторинга (опционально)
read -p "📊 Разрешить порты для мониторинга? (9090, 3000) (y/N): " MONITORING
if [[ $MONITORING =~ ^[Yy]$ ]]; then
    ufw allow 9090/tcp comment 'Prometheus'
    ufw allow 3000/tcp comment 'Grafana'
    echo "✅ Порты мониторинга разрешены"
fi

# Включение логирования
echo "📝 Включение логирования..."
ufw logging on

# Включение firewall
echo "🔥 Включение firewall..."
ufw --force enable

# Показать статус
echo ""
echo "📊 Статус firewall:"
ufw status verbose

echo ""
echo "✅ Firewall настроен!"
echo ""
echo "📋 Открытые порты:"
echo "   - 22/tcp  (SSH)"
echo "   - 80/tcp  (HTTP)"
echo "   - 443/tcp (HTTPS)"
echo ""
echo "🔒 Закрытые порты:"
echo "   - 5432/tcp (PostgreSQL)"
echo "   - 6379/tcp (Redis)"
echo "   - 8000/tcp (Bot Server)"
echo ""
echo "📝 Логи firewall:"
echo "   - tail -f /var/log/ufw.log"
echo ""
echo "🔧 Управление:"
echo "   - Статус: ufw status"
echo "   - Отключить: ufw disable"
echo "   - Включить: ufw enable"
echo "   - Сброс: ufw --force reset"
