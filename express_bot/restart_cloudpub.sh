#!/bin/bash

echo "🔄 Перезапуск CloudPub для Express Bot..."

# 1. Проверяем текущий статус
echo "1️⃣ Проверяем текущий статус..."
sudo clo ls

# 2. Удаляем старый сервис (если есть)
echo "2️⃣ Удаляем старый сервис..."
sudo clo remove express-bot 2>/dev/null || echo "Сервис не найден"

# 3. Регистрируем новый сервис
echo "3️⃣ Регистрируем новый сервис..."
sudo -H clo register --name express-bot http localhost:5011

# 4. Проверяем результат
echo "4️⃣ Проверяем результат..."
sudo clo ls

# 5. Тестируем подключение
echo "5️⃣ Тестируем подключение..."
sleep 3
curl -s https://loosely-welcoming-grackle.cloudpub.ru/health | head -3

echo ""
echo "✅ CloudPub перезапущен!"
echo "🌐 URL: https://loosely-welcoming-grackle.cloudpub.ru"
echo "🔗 Webhook: https://loosely-welcoming-grackle.cloudpub.ru/webhook"

