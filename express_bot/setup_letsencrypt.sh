#!/bin/bash

echo "🔐 Настройка Let's Encrypt SSL для Express.ms Bot"
echo "================================================"

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

# Проверка доступности домена
echo "🔍 Проверка доступности домена..."
if ! ping -c 1 "$DOMAIN" > /dev/null 2>&1; then
    echo "❌ Домен $DOMAIN недоступен. Убедитесь, что DNS настроен правильно."
    exit 1
fi

echo "✅ Домен $DOMAIN доступен"

# Установка certbot
echo "📦 Установка certbot..."
if ! command -v certbot &> /dev/null; then
    apt update
    apt install -y certbot
    echo "✅ Certbot установлен"
else
    echo "✅ Certbot уже установлен"
fi

# Остановка nginx для получения сертификата
echo "🛑 Остановка nginx..."
systemctl stop nginx 2>/dev/null || true
docker-compose stop nginx 2>/dev/null || true

# Получение сертификата
echo "🔐 Получение SSL сертификата от Let's Encrypt..."
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domains "$DOMAIN"

if [ $? -eq 0 ]; then
    echo "✅ SSL сертификат получен успешно"
else
    echo "❌ Ошибка получения SSL сертификата"
    exit 1
fi

# Копирование сертификатов
echo "📋 Копирование сертификатов..."
mkdir -p ssl
cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ssl/cert.pem
cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ssl/key.pem
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem

echo "✅ Сертификаты скопированы в ssl/"

# Создание скрипта обновления сертификатов
echo "🔄 Создание скрипта обновления сертификатов..."
cat > update_ssl.sh << EOF
#!/bin/bash

echo "🔄 Обновление SSL сертификатов..."

# Обновление сертификатов
certbot renew --quiet

if [ \$? -eq 0 ]; then
    echo "✅ Сертификаты обновлены"
    
    # Копирование новых сертификатов
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ssl/cert.pem
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ssl/key.pem
    chmod 644 ssl/cert.pem
    chmod 600 ssl/key.pem
    
    # Перезапуск nginx
    docker-compose restart nginx
    
    echo "✅ SSL сертификаты обновлены и nginx перезапущен"
else
    echo "❌ Ошибка обновления сертификатов"
fi
EOF

chmod +x update_ssl.sh

# Настройка cron для автоматического обновления
echo "⏰ Настройка автоматического обновления сертификатов..."
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/express/bots/production/update_ssl.sh") | crontab -

# Создание Nginx конфигурации с Let's Encrypt
echo "🌐 Создание Nginx конфигурации с Let's Encrypt..."
cat > nginx-letsencrypt.conf << EOF
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
        
        # SSL конфигурация (Let's Encrypt)
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
cp nginx-letsencrypt.conf nginx.conf

echo "✅ Let's Encrypt SSL настроен!"
echo "🌐 Домен: $DOMAIN"
echo "📧 Email: $EMAIL"
echo "🔐 Сертификат: ssl/cert.pem"
echo "🔑 Приватный ключ: ssl/key.pem"
echo ""
echo "📋 Следующие шаги:"
echo "1. Запустите бота: docker-compose up -d"
echo "2. Проверьте SSL: curl -I https://$DOMAIN/health"
echo "3. Настройте webhook в Express.ms: https://$DOMAIN/webhook"
echo ""
echo "🔄 Автоматическое обновление сертификатов настроено (cron)"
echo "📋 Скрипт обновления: ./update_ssl.sh"
