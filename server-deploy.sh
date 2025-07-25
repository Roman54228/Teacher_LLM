#!/bin/bash
# Скрипт развертывания на сервере (запускать на сервере после копирования кода)

set -e

echo "🚀 Развертывание Telegram Mini App на сервере"
echo "============================================="

# Проверка что мы на сервере
if [ ! -f "telegram_app.py" ]; then
    echo "❌ Файл telegram_app.py не найден!"
    echo "Убедитесь что вы запускаете скрипт в папке с кодом приложения"
    exit 1
fi

# Получение домена от пользователя
read -p "Введите ваш домен (например: myapp.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Домен не указан!"
    exit 1
fi

echo "Домен: $DOMAIN"
echo

# 1. Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# 2. Установка необходимых пакетов
echo "🔧 Установка зависимостей..."
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# 3. Создание пользователя webapp
echo "👤 Создание пользователя webapp..."
if ! id "webapp" &>/dev/null; then
    adduser --disabled-password --gecos "" webapp
    usermod -aG sudo webapp
    echo "✅ Пользователь webapp создан"
else
    echo "✅ Пользователь webapp уже существует"
fi

# 4. Копирование файлов в домашнюю папку webapp
echo "📁 Копирование файлов приложения..."
sudo -u webapp mkdir -p /home/webapp/telegram-mini-app
cp -r * /home/webapp/telegram-mini-app/
chown -R webapp:webapp /home/webapp/telegram-mini-app

# Копируем важные файлы конфигурации
echo "📝 Копирование config.yaml..."
if [ -f "config.yaml" ]; then
    cp config.yaml /home/webapp/telegram-mini-app/
    chown webapp:webapp /home/webapp/telegram-mini-app/config.yaml
fi

# 5. Настройка Python окружения
echo "🐍 Настройка Python окружения..."
sudo -u webapp bash << 'WEBAPP_SETUP'
cd /home/webapp/telegram-mini-app

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements-production.txt

# Создание директорий
mkdir -p logs static data

# Создание .env файла
cat > .env << 'ENV_EOF'
# Telegram Bot (ЗАПОЛНИТЕ СВОИ ДАННЫЕ ПОСЛЕ УСТАНОВКИ)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# YandexGPT API (ЗАПОЛНИТЕ СВОИ ДАННЫЕ ПОСЛЕ УСТАНОВКИ)
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id

# Database
DATABASE_URL=sqlite:///interview_prep.db

# Production settings
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Domain
DOMAIN=$DOMAIN
ENV_EOF

echo "✅ Python окружение настроено"
WEBAPP_SETUP

# 6. Создание systemd сервиса
echo "⚙️ Настройка systemd сервиса..."
cat > /etc/systemd/system/telegram-mini-app.service << 'SERVICE_EOF'
[Unit]
Description=Telegram Mini App
After=network.target

[Service]
Type=simple
User=webapp
WorkingDirectory=/home/webapp/telegram-mini-app
Environment=PATH=/home/webapp/telegram-mini-app/venv/bin
ExecStart=/home/webapp/telegram-mini-app/venv/bin/python production_app.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 7. Настройка Nginx
echo "🌐 Настройка Nginx..."
cat > /etc/nginx/sites-available/telegram-mini-app << NGINX_EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket поддержка
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Увеличиваем таймауты
        proxy_connect_timeout       60s;
        proxy_send_timeout          60s;
        proxy_read_timeout          60s;
    }

    # Статические файлы
    location /static/ {
        alias /home/webapp/telegram-mini-app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Безопасность
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
NGINX_EOF

# Активация конфигурации Nginx
ln -sf /etc/nginx/sites-available/telegram-mini-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Удаляем дефолтный сайт
nginx -t
systemctl reload nginx

# 8. Запуск сервиса
echo "🚀 Запуск приложения..."
systemctl daemon-reload
systemctl enable telegram-mini-app
systemctl start telegram-mini-app

# 9. SSL сертификат (пропускаем автоматическое получение)
echo "🔒 SSL сертификат..."
echo "ℹ️  SSL сертификат пропущен (настройте вручную при необходимости)"
echo "Команда для ручной настройки: certbot --nginx -d $DOMAIN -d www.$DOMAIN"

# 10. Настройка файрвола
echo "🔥 Настройка файрвола..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

# 11. Финальная проверка
echo "✅ Проверка статуса..."
sleep 3
systemctl status telegram-mini-app --no-pager

echo
echo "🎉 Развертывание завершено!"
echo "==============================================="
echo "Следующие шаги:"
echo "1. Отредактируйте /home/webapp/telegram-mini-app/.env"
echo "2. Добавьте ваши API ключи (TELEGRAM_BOT_TOKEN, YANDEX_API_KEY, YANDEX_FOLDER_ID)"
echo "3. Перезапустите приложение: systemctl restart telegram-mini-app"
echo "4. Настройте URL в @BotFather: https://$DOMAIN"
echo
echo "Приложение доступно по адресу: https://$DOMAIN"
echo
echo "Полезные команды:"
echo "  systemctl status telegram-mini-app     # Статус"
echo "  systemctl restart telegram-mini-app    # Перезапуск"
echo "  journalctl -u telegram-mini-app -f     # Логи"
echo "  nano /home/webapp/telegram-mini-app/.env  # Редактирование настроек"
echo
echo "Файлы приложения: /home/webapp/telegram-mini-app/"