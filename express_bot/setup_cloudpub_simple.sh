#!/bin/bash

echo "🚀 Настройка CloudPub для Express Bot..."

# 1. Устанавливаем CloudPub
echo "1️⃣ Устанавливаем CloudPub..."
export CLO_VERSION="2.2.2"
sudo mkdir -p /usr/local/bin && cd /usr/local/bin
sudo curl -L "https://cloudpub.ru/download/stable/clo-${CLO_VERSION}-stable-linux-$(uname -m).tar.gz" | sudo tar -xzv
sudo chmod +x clo

# 2. Настраиваем токен
echo "2️⃣ Настраиваем токен..."
sudo -H clo set token GCJBOg6PyZWdn6r4oeT0tYM2WpVpUkclJwsXR0bDNQU

# 3. Проверяем статус
echo "3️⃣ Проверяем статус..."
sudo clo status

# 4. Регистрируем Express Bot
echo "4️⃣ Регистрируем Express Bot..."
sudo -H clo register --name express-bot http localhost:5011

# 5. Запускаем сервис
echo "5️⃣ Запускаем сервис..."
sudo systemctl enable --now clo.service

# 6. Проверяем сервисы
echo "6️⃣ Проверяем сервисы..."
sudo clo list

echo ""
echo "🎉 CloudPub настроен!"
echo "📋 Следующие шаги:"
echo "1. Проверьте URL: sudo clo list"
echo "2. Обновите конфигурацию с новым URL"
echo "3. Настройте webhook в Express.ms"

