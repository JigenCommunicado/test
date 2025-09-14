#!/bin/bash

echo "🔐 Настройка SSL сертификатов для Express.ms Bot"
echo "================================================"

# Создание директории для SSL
mkdir -p ssl

# Проверка наличия существующих сертификатов
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo "✅ SSL сертификаты уже существуют"
    echo "📋 Сертификат: ssl/cert.pem"
    echo "🔑 Приватный ключ: ssl/key.pem"
    exit 0
fi

echo "🔧 Генерация самоподписанного сертификата..."

# Генерация приватного ключа
openssl genrsa -out ssl/key.pem 2048

# Генерация сертификата
openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 -subj "/C=RU/ST=Moscow/L=Moscow/O=Express.ms Bot/OU=IT Department/CN=localhost"

# Установка правильных прав доступа
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "✅ SSL сертификаты созданы:"
echo "📋 Сертификат: ssl/cert.pem"
echo "🔑 Приватный ключ: ssl/key.pem"
echo ""
echo "⚠️  ВНИМАНИЕ: Это самоподписанный сертификат!"
echo "   Для production используйте сертификат от доверенного CA"
echo "   (Let's Encrypt, DigiCert, etc.)"
echo ""
echo "🔧 Для Let's Encrypt используйте:"
echo "   certbot certonly --standalone -d your-domain.com"
echo "   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem"
echo "   cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem"
