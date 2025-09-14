#!/bin/bash

echo "🔍 Проверка DNS для Express.ms Bot"
echo "================================="

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "❌ Использование: $0 <domain>"
    echo "Пример: $0 bot.yourcompany.com"
    exit 1
fi

DOMAIN=$1

echo "🌐 Проверка домена: $DOMAIN"
echo ""

# Проверка A-записи
echo "1️⃣ Проверка A-записи..."
A_RECORD=$(dig +short $DOMAIN A)
if [ -n "$A_RECORD" ]; then
    echo "✅ A-запись: $A_RECORD"
else
    echo "❌ A-запись не найдена"
fi

# Проверка AAAA-записи (IPv6)
echo ""
echo "2️⃣ Проверка AAAA-записи (IPv6)..."
AAAA_RECORD=$(dig +short $DOMAIN AAAA)
if [ -n "$AAAA_RECORD" ]; then
    echo "✅ AAAA-запись: $AAAA_RECORD"
else
    echo "ℹ️  AAAA-запись не найдена (не критично)"
fi

# Проверка CNAME-записи
echo ""
echo "3️⃣ Проверка CNAME-записи..."
CNAME_RECORD=$(dig +short $DOMAIN CNAME)
if [ -n "$CNAME_RECORD" ]; then
    echo "✅ CNAME-запись: $CNAME_RECORD"
else
    echo "ℹ️  CNAME-запись не найдена (не критично)"
fi

# Проверка MX-записи
echo ""
echo "4️⃣ Проверка MX-записи..."
MX_RECORD=$(dig +short $DOMAIN MX)
if [ -n "$MX_RECORD" ]; then
    echo "✅ MX-запись: $MX_RECORD"
else
    echo "ℹ️  MX-запись не найдена (не критично)"
fi

# Проверка TXT-записи
echo ""
echo "5️⃣ Проверка TXT-записи..."
TXT_RECORD=$(dig +short $DOMAIN TXT)
if [ -n "$TXT_RECORD" ]; then
    echo "✅ TXT-запись: $TXT_RECORD"
else
    echo "ℹ️  TXT-запись не найдена (не критично)"
fi

# Проверка NS-записей
echo ""
echo "6️⃣ Проверка NS-записей..."
NS_RECORDS=$(dig +short $DOMAIN NS)
if [ -n "$NS_RECORDS" ]; then
    echo "✅ NS-записи:"
    echo "$NS_RECORDS" | while read ns; do
        echo "   - $ns"
    done
else
    echo "❌ NS-записи не найдены"
fi

# Проверка SOA-записи
echo ""
echo "7️⃣ Проверка SOA-записи..."
SOA_RECORD=$(dig +short $DOMAIN SOA)
if [ -n "$SOA_RECORD" ]; then
    echo "✅ SOA-запись: $SOA_RECORD"
else
    echo "❌ SOA-запись не найдена"
fi

# Проверка доступности домена
echo ""
echo "8️⃣ Проверка доступности домена..."
if ping -c 1 "$DOMAIN" > /dev/null 2>&1; then
    echo "✅ Домен $DOMAIN доступен"
else
    echo "❌ Домен $DOMAIN недоступен"
fi

# Проверка HTTP/HTTPS
echo ""
echo "9️⃣ Проверка HTTP/HTTPS..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null)
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null)

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
    echo "✅ HTTP доступен (статус: $HTTP_STATUS)"
else
    echo "❌ HTTP недоступен (статус: $HTTP_STATUS)"
fi

if [ "$HTTPS_STATUS" = "200" ] || [ "$HTTPS_STATUS" = "301" ] || [ "$HTTPS_STATUS" = "302" ]; then
    echo "✅ HTTPS доступен (статус: $HTTPS_STATUS)"
else
    echo "❌ HTTPS недоступен (статус: $HTTPS_STATUS)"
fi

# Проверка SSL сертификата
echo ""
echo "🔟 Проверка SSL сертификата..."
SSL_INFO=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
if [ -n "$SSL_INFO" ]; then
    echo "✅ SSL сертификат найден:"
    echo "$SSL_INFO" | while read line; do
        echo "   $line"
    done
else
    echo "❌ SSL сертификат не найден или недействителен"
fi

# Получение IP адреса сервера
echo ""
echo "🖥️  IP адрес этого сервера:"
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || hostname -I | awk '{print $1}')
if [ -n "$SERVER_IP" ]; then
    echo "✅ Сервер IP: $SERVER_IP"
    
    # Сравнение с A-записью
    if [ "$A_RECORD" = "$SERVER_IP" ]; then
        echo "✅ A-запись соответствует IP сервера"
    else
        echo "⚠️  A-запись ($A_RECORD) не соответствует IP сервера ($SERVER_IP)"
        echo "   Настройте A-запись для $DOMAIN на $SERVER_IP"
    fi
else
    echo "❌ Не удалось получить IP адрес сервера"
fi

echo ""
echo "📋 Рекомендации:"
echo "1. Убедитесь, что A-запись для $DOMAIN указывает на $SERVER_IP"
echo "2. Дождитесь распространения DNS (может занять до 24 часов)"
echo "3. Проверьте настройки firewall на сервере"
echo "4. Убедитесь, что порты 80 и 443 открыты"
echo "5. Для production используйте Let's Encrypt SSL"
