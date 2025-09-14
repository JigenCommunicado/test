# 🌐🔐 Настройка домена и SSL для Express.ms Bot

## 📋 Пункт 2: Настройка домена и SSL сертификата

### 🚀 **Быстрый старт:**

#### **Автоматическая настройка:**
```bash
sudo chmod +x setup_domain_ssl.sh
sudo ./setup_domain_ssl.sh bot.yourcompany.com admin@yourcompany.com
```

#### **Ручная настройка:**
```bash
# 1. Настройка домена
sudo ./setup_domain.sh bot.yourcompany.com

# 2. Настройка SSL (выберите один вариант)
sudo ./setup_letsencrypt.sh bot.yourcompany.com admin@yourcompany.com  # Let's Encrypt
sudo ./setup_ssl_domain.sh bot.yourcompany.com                          # Самоподписанный

# 3. Проверка DNS
./check_dns.sh bot.yourcompany.com

# 4. Настройка Firewall
sudo ./setup_firewall.sh
```

### 🔐 **Типы SSL сертификатов:**

#### **1. Let's Encrypt (рекомендуется для production):**
- ✅ Бесплатный
- ✅ Автоматическое обновление
- ✅ Доверенный всеми браузерами
- ❌ Требует доступный домен
- ❌ Ограничения по количеству запросов

```bash
sudo ./setup_letsencrypt.sh bot.yourcompany.com admin@yourcompany.com
```

#### **2. Самоподписанный (для тестирования):**
- ✅ Работает сразу
- ✅ Не требует внешнего доступа
- ❌ Предупреждения в браузере
- ❌ Не подходит для production

```bash
sudo ./setup_ssl_domain.sh bot.yourcompany.com
```

### 🌐 **Настройка DNS:**

#### **Требуемые записи:**
```
A-запись:    bot.yourcompany.com    →    YOUR_SERVER_IP
CNAME:       www.bot.yourcompany.com →    bot.yourcompany.com
```

#### **Проверка DNS:**
```bash
# Проверка A-записи
dig +short bot.yourcompany.com A

# Проверка доступности
ping bot.yourcompany.com

# Проверка HTTP/HTTPS
curl -I http://bot.yourcompany.com
curl -I https://bot.yourcompany.com
```

### 🔥 **Настройка Firewall:**

#### **Открытые порты:**
- **22/tcp** - SSH
- **80/tcp** - HTTP
- **443/tcp** - HTTPS

#### **Закрытые порты:**
- **5432/tcp** - PostgreSQL (внутренний)
- **6379/tcp** - Redis (внутренний)
- **8000/tcp** - Bot Server (внутренний)

#### **Управление:**
```bash
# Статус
sudo ufw status

# Отключить
sudo ufw disable

# Включить
sudo ufw enable

# Сброс
sudo ufw --force reset
```

### 📊 **Мониторинг и диагностика:**

#### **Проверка SSL сертификата:**
```bash
# Информация о сертификате
openssl x509 -in ssl/cert.pem -text -noout

# Проверка подключения
openssl s_client -connect bot.yourcompany.com:443 -servername bot.yourcompany.com

# Проверка срока действия
openssl x509 -in ssl/cert.pem -noout -dates
```

#### **Проверка Nginx:**
```bash
# Тест конфигурации
nginx -t

# Перезапуск
docker-compose restart nginx

# Логи
docker-compose logs nginx
```

#### **Проверка бота:**
```bash
# Health check
curl https://bot.yourcompany.com/health

# Webhook test
curl -X POST https://bot.yourcompany.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "user_id": "test", "text": "/start"}'
```

### 🔄 **Обновление SSL сертификатов:**

#### **Let's Encrypt (автоматическое):**
```bash
# Ручное обновление
sudo ./update_ssl.sh

# Проверка cron
crontab -l

# Логи обновления
grep certbot /var/log/syslog
```

#### **Самоподписанный (ручное):**
```bash
# Генерация нового сертификата
sudo ./setup_ssl_domain.sh bot.yourcompany.com

# Перезапуск nginx
docker-compose restart nginx
```

### 🚨 **Устранение неполадок:**

#### **Проблемы с DNS:**
```bash
# Проверка DNS
./check_dns.sh bot.yourcompany.com

# Очистка DNS кэша
sudo systemctl flush-dns  # Ubuntu/Debian
sudo dscacheutil -flushcache  # macOS
ipconfig /flushdns  # Windows
```

#### **Проблемы с SSL:**
```bash
# Проверка сертификата
openssl x509 -in ssl/cert.pem -text -noout

# Проверка ключа
openssl rsa -in ssl/key.pem -check

# Проверка подключения
curl -v https://bot.yourcompany.com/health
```

#### **Проблемы с Firewall:**
```bash
# Проверка статуса
sudo ufw status verbose

# Проверка логов
sudo tail -f /var/log/ufw.log

# Проверка портов
sudo netstat -tlnp | grep -E "(80|443|22)"
```

#### **Проблемы с Nginx:**
```bash
# Тест конфигурации
docker exec express-bot-nginx nginx -t

# Логи ошибок
docker-compose logs nginx

# Перезапуск
docker-compose restart nginx
```

### 📋 **Checklist для настройки:**

- [ ] Домен зарегистрирован и настроен
- [ ] DNS записи настроены (A-запись на IP сервера)
- [ ] Firewall настроен (порты 80, 443 открыты)
- [ ] SSL сертификат получен и настроен
- [ ] Nginx конфигурация обновлена
- [ ] Бот запущен и доступен
- [ ] Health check проходит успешно
- [ ] Webhook доступен извне
- [ ] Автоматическое обновление SSL настроено
- [ ] Мониторинг настроен

### 🌐 **Примеры конфигурации:**

#### **Nginx для Let's Encrypt:**
```nginx
server {
    listen 443 ssl http2;
    server_name bot.yourcompany.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://express-bot:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### **Cron для обновления SSL:**
```bash
# Обновление SSL каждый день в 3:00
0 3 * * * /opt/express/bots/production/update_ssl.sh
```

### 📞 **Поддержка:**

- **Let's Encrypt**: https://letsencrypt.org/docs/
- **Nginx**: https://nginx.org/en/docs/
- **UFW**: https://help.ubuntu.com/community/UFW
- **Express.ms**: support@express.ms

### ⚠️ **Важные замечания:**

1. **Дождитесь распространения DNS** (до 24 часов)
2. **Используйте Let's Encrypt для production**
3. **Настройте автоматическое обновление SSL**
4. **Мониторьте срок действия сертификатов**
5. **Тестируйте webhook извне**
6. **Настройте мониторинг доступности**
