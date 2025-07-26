#!/bin/bash
# Простой скрипт развертывания (работает в текущей директории)

set -e

echo "🚀 Простое развертывание Telegram Mini App (FastAPI)"
echo "=================================================="

# Проверка что мы в правильной папке
if [ ! -f "main.py" ]; then
    echo "❌ Файл main.py не найден!"
    echo "Запускайте скрипт в папке с кодом приложения"
    exit 1
fi

# Получение домена
read -p "Введите ваш домен (например: filonov.space): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Домен не указан!"
    exit 1
fi

echo "Домен: $DOMAIN"
echo

# 1. Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# 2. Установка зависимостей
echo "🔧 Установка зависимостей..."
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# 3. Настройка Python окружения
echo "🐍 Настройка Python окружения..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-production.txt

# Создание директорий
mkdir -p logs static data

# 4. Создание .env файла
echo "⚙️ Создание конфигурации..."
cat > .env << ENV_EOF
# Telegram Bot (ЗАПОЛНИТЕ СВОИ ДАННЫЕ)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# YandexGPT API (ЗАПОЛНИТЕ СВОИ ДАННЫЕ)
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id

# Database
DATABASE_URL=sqlite:///interview_prep.db

# Production settings
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=5002

# Domain
DOMAIN=$DOMAIN
ENV_EOF

# 5. Создание systemd сервиса
echo "⚙️ Настройка systemd сервиса..."
CURRENT_DIR=$(pwd)
cat > /etc/systemd/system/telegram-mini-app.service << SERVICE_EOF
[Unit]
Description=Telegram Mini App (FastAPI)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python main.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 6. Настройка Nginx
echo "🌐 Настройка Nginx..."
cat > /etc/nginx/sites-available/telegram-mini-app << NGINX_EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5002;
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
        alias $CURRENT_DIR/static/;
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
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# 7. Запуск сервиса
echo "🚀 Запуск приложения..."
systemctl daemon-reload
systemctl enable telegram-mini-app
systemctl start telegram-mini-app

# 8. SSL (пропускаем автоматическое получение)
echo "🔒 SSL сертификат..."
echo "ℹ️  Команда для получения SSL: certbot --nginx -d $DOMAIN -d www.$DOMAIN"

# 9. Настройка файрвола
echo "🔥 Настройка файрвола..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

# 10. Проверка статуса
echo "✅ Проверка статуса..."
sleep 3
systemctl status telegram-mini-app --no-pager

echo
echo "🎉 Развертывание завершено!"
echo "========================="
echo "Приложение установлено в: $(pwd)"
echo "FastAPI приложение запущено на порту 5002"
echo "Документация API: https://$DOMAIN/docs"
echo
echo "Следующие шаги:"
echo "1. Отредактируйте .env и добавьте ваши API ключи"
echo "2. Перезапустите: systemctl restart telegram-mini-app"
echo "3. Получите SSL: certbot --nginx -d $DOMAIN"
echo "4. Настройте @BotFather: https://$DOMAIN"
echo
echo "Полезные команды:"
echo "  systemctl status telegram-mini-app"
echo "  systemctl restart telegram-mini-app"
echo "  journalctl -u telegram-mini-app -f"
echo "  nano .env"