#!/bin/bash

echo "🌐🔐 Мастер настройки домена и SSL для Express.ms Bot"
echo "=================================================="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo $0"
    exit 1
fi

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "❌ Использование: $0 <domain> [email]"
    echo "Пример: $0 bot.yourcompany.com admin@yourcompany.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

echo "🌐 Домен: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# Меню выбора типа SSL
echo "🔐 Выберите тип SSL сертификата:"
echo "1) Let's Encrypt (рекомендуется для production)"
echo "2) Самоподписанный (для тестирования)"
echo "3) Пропустить SSL (только HTTP)"
echo ""
read -p "Введите номер (1-3): " SSL_CHOICE

case $SSL_CHOICE in
    1)
        echo "🔐 Настройка Let's Encrypt SSL..."
        chmod +x setup_letsencrypt.sh
        ./setup_letsencrypt.sh "$DOMAIN" "$EMAIL"
        ;;
    2)
        echo "🔐 Настройка самоподписанного SSL..."
        chmod +x setup_ssl_domain.sh
        ./setup_ssl_domain.sh "$DOMAIN"
        ;;
    3)
        echo "⚠️  SSL пропущен. Будет использоваться только HTTP."
        chmod +x setup_domain.sh
        ./setup_domain.sh "$DOMAIN"
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "🔍 Проверка DNS..."
chmod +x check_dns.sh
./check_dns.sh "$DOMAIN"

echo ""
echo "🔥 Настройка Firewall..."
chmod +x setup_firewall.sh
./setup_firewall.sh

echo ""
echo "📋 Следующие шаги:"
echo "1. Убедитесь, что DNS настроен правильно"
echo "2. Дождитесь распространения DNS (до 24 часов)"
echo "3. Запустите бота: docker-compose up -d"
echo "4. Проверьте доступность: curl -I https://$DOMAIN/health"
echo "5. Настройте webhook в Express.ms: https://$DOMAIN/webhook"
echo ""
echo "🌐 Ваши URL:"
echo "   - HTTP: http://$DOMAIN"
echo "   - HTTPS: https://$DOMAIN"
echo "   - Health: https://$DOMAIN/health"
echo "   - Webhook: https://$DOMAIN/webhook"
echo "   - Admin: https://$DOMAIN/admin"
echo ""
echo "📞 Для получения BOT_CREDENTIALS обратитесь к разработчикам Express.ms"
