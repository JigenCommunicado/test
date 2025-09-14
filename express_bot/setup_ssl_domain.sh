#!/bin/bash

echo "🔐 Настройка самоподписанного SSL для Express.ms Bot"
echo "=================================================="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo $0"
    exit 1
fi

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "❌ Использование: $0 <domain>"
    echo "Пример: $0 bot.yourcompany.com"
    exit 1
fi

DOMAIN=$1

echo "🌐 Домен: $DOMAIN"

# Создание директории для SSL
mkdir -p ssl

# Проверка наличия существующих сертификатов
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo "⚠️  SSL сертификаты уже существуют"
    read -p "Перезаписать? (y/N): " OVERWRITE
    if [[ ! $OVERWRITE =~ ^[Yy]$ ]]; then
        echo "❌ Отменено"
        exit 0
    fi
fi

echo "🔧 Генерация самоподписанного сертификата для $DOMAIN..."

# Создание конфигурации для сертификата
cat > ssl/cert.conf << EOF
[req]
default_bits = 2048
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
C=RU
ST=Moscow
L=Moscow
O=Express.ms Bot
OU=IT Department
CN=$DOMAIN
emailAddress=admin@$DOMAIN

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = *.$DOMAIN
EOF

# Генерация приватного ключа
openssl genrsa -out ssl/key.pem 2048

# Генерация запроса на сертификат
openssl req -new -key ssl/key.pem -out ssl/cert.csr -config ssl/cert.conf

# Генерация самоподписанного сертификата
openssl x509 -req -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem -days 365 -extensions v3_req -extfile ssl/cert.conf

# Удаление временных файлов
rm ssl/cert.csr ssl/cert.conf

# Установка правильных прав доступа
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "✅ Самоподписанный SSL сертификат создан:"
echo "📋 Сертификат: ssl/cert.pem"
echo "🔑 Приватный ключ: ssl/key.pem"
echo "🌐 Домен: $DOMAIN"
echo "📅 Срок действия: 365 дней"

# Создание Nginx конфигурации с самоподписанным сертификатом
echo "🌐 Создание Nginx конфигурации..."
cat > nginx-selfsigned.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Логирование
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Основные настройки
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;
    
    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=webhook:10m rate=5r/s;
    
    # Upstream для бота
    upstream express_bot {
        server express-bot:8000;
        keepalive 32;
    }
    
    # HTTP сервер (редирект на HTTPS)
    server {
        listen 80;
        server_name $DOMAIN;
        
        # Редирект на HTTPS
        return 301 https://\$host\$request_uri;
    }
    
    # HTTPS сервер
    server {
        listen 443 ssl http2;
        server_name $DOMAIN;
        
        # SSL конфигурация (самоподписанный)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Health check endpoint
        location /health {
            proxy_pass http://express_bot;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Кэширование health check
            proxy_cache_valid 200 30s;
        }
        
        # Webhook endpoint (с rate limiting)
        location /webhook {
            limit_req zone=webhook burst=20 nodelay;
            
            proxy_pass http://express_bot;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Таймауты для webhook
            proxy_connect_timeout 5s;
            proxy_send_timeout 10s;
            proxy_read_timeout 10s;
        }
        
        # API endpoints (с rate limiting)
        location /api/ {
            limit_req zone=api burst=50 nodelay;
            
            proxy_pass http://express_bot;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Статические файлы
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Все остальные запросы
        location / {
            proxy_pass http://express_bot;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Таймауты
            proxy_connect_timeout 5s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Логирование
        access_log /var/log/nginx/express_bot_access.log main;
        error_log /var/log/nginx/express_bot_error.log;
    }
}
EOF

# Замена nginx.conf
cp nginx-selfsigned.conf nginx.conf

echo "✅ Nginx конфигурация создана"
echo "🌐 Домен: $DOMAIN"
echo "📋 Файл: nginx.conf обновлен"
echo ""
echo "⚠️  ВНИМАНИЕ: Это самоподписанный сертификат!"
echo "   Браузеры будут показывать предупреждение о безопасности"
echo "   Для production используйте Let's Encrypt: ./setup_letsencrypt.sh $DOMAIN"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте DNS для домена $DOMAIN"
echo "2. Укажите A-запись на IP этого сервера"
echo "3. Запустите бота: docker-compose up -d"
echo "4. Проверьте SSL: curl -k https://$DOMAIN/health"
echo "5. Настройте webhook в Express.ms: https://$DOMAIN/webhook"
