#!/bin/bash
# Быстрое развертывание Telegram Mini App

set -e  # Exit on any error

echo "🚀 Развертывание Telegram Mini App"
echo "=================================="

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo "Использование: $0 <domain> [user@server]"
    echo "Пример для локального тестирования: $0 localhost"
    echo "Пример для сервера: $0 myapp.com webapp@192.168.1.100"
    exit 1
fi

DOMAIN=$1
SERVER=${2:-"localhost"}

echo "Домен: $DOMAIN"
if [ "$SERVER" != "localhost" ]; then
    echo "Сервер: $SERVER"
else
    echo "Режим: Локальное развертывание"
fi
echo

# Проверка режима развертывания
if [ "$SERVER" = "localhost" ]; then
    echo "🔧 Локальная настройка..."
    
    # Создание виртуального окружения
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Установка зависимостей
    echo "📋 Установка зависимостей..."
    pip install -r requirements-production.txt
    
    # Создание директорий
    mkdir -p logs static data
    
    # Создание локального конфигурационного файла
    echo "⚙️ Создание конфигурации..."
    cat > .env << 'ENV_EOF'
# Telegram Bot (ЗАПОЛНИТЕ СВОИ ДАННЫЕ)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# YandexGPT API (ЗАПОЛНИТЕ СВОИ ДАННЫЕ)  
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id

# Database
DATABASE_URL=sqlite:///interview_prep.db

# Local development settings
FLASK_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Domain
DOMAIN=$DOMAIN
ENV_EOF

    echo "✅ Локальная настройка завершена!"
    echo
    echo "Следующие шаги:"
    echo "1. Отредактируйте файл .env и добавьте ваши API ключи"
    echo "2. Запустите приложение: source venv/bin/activate && python production_app.py"
    echo "3. Откройте http://localhost:5000 в браузере"
    echo
    exit 0
fi

# 1. Создание архива проекта для удаленного сервера
echo "📦 Создание архива проекта..."
tar -czf telegram-mini-app.tar.gz \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='interview_prep.db' \
    --exclude='logs' \
    *.py *.md *.txt *.yaml *.yml templates/ utils/ data/ static/ 2>/dev/null || true

echo "✅ Архив создан"

# 2. Загрузка на сервер
echo "📤 Загрузка файлов на сервер..."
scp telegram-mini-app.tar.gz $SERVER:/tmp/

# 3. Выполнение команд на сервере
echo "🔧 Настройка на сервере..."
ssh $SERVER << EOF
set -e

# Создание пользователя webapp если не существует
if ! id "webapp" &>/dev/null; then
    sudo adduser --disabled-password --gecos "" webapp
    sudo usermod -aG sudo webapp
    echo "✅ Пользователь webapp создан"
fi

# Переключение на пользователя webapp
sudo -u webapp bash << 'WEBAPP_EOF'
cd /home/webapp

# Создание директории приложения
rm -rf telegram-mini-app
mkdir -p telegram-mini-app
cd telegram-mini-app

# Распаковка архива
tar -xzf /tmp/telegram-mini-app.tar.gz

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements-production.txt

# Создание директорий
mkdir -p logs static data

# Создание конфигурационного файла
cat > .env << 'ENV_EOF'
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
PORT=5000

# Domain
DOMAIN=$DOMAIN
ENV_EOF

echo "✅ Приложение настроено в /home/webapp/telegram-mini-app"
WEBAPP_EOF

# Настройка системного сервиса
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

# Настройка Nginx
cat > /etc/nginx/sites-available/telegram-mini-app << 'NGINX_EOF'
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
nginx -t && systemctl reload nginx

# Запуск сервиса
systemctl daemon-reload
systemctl enable telegram-mini-app
systemctl start telegram-mini-app

echo "✅ Системный сервис настроен и запущен"

# Установка SSL сертификата
if command -v certbot &> /dev/null; then
    echo "🔒 Установка SSL сертификата..."
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || true
    echo "✅ SSL сертификат установлен"
else
    echo "⚠️  Certbot не установлен. Установите SSL вручную:"
    echo "   sudo apt install certbot python3-certbot-nginx"
    echo "   sudo certbot --nginx -d $DOMAIN"
fi

# Очистка
rm -f /tmp/telegram-mini-app.tar.gz

EOF

# Очистка локальных файлов
rm -f telegram-mini-app.tar.gz

echo
echo "🎉 Развертывание завершено!"
echo "=================================================="
echo "Следующие шаги:"
echo "1. Зайдите на сервер и отредактируйте /home/webapp/telegram-mini-app/.env"
echo "2. Добавьте ваши API ключи (TELEGRAM_BOT_TOKEN, YANDEX_API_KEY, YANDEX_FOLDER_ID)"
echo "3. Перезапустите сервис: sudo systemctl restart telegram-mini-app"
echo "4. Проверьте статус: sudo systemctl status telegram-mini-app"
echo "5. Настройте URL в @BotFather: https://$DOMAIN"
echo
echo "Полезные команды на сервере:"
echo "- Логи приложения: sudo journalctl -u telegram-mini-app -f"
echo "- Перезапуск: sudo systemctl restart telegram-mini-app"
echo "- Статус: sudo systemctl status telegram-mini-app"
echo "- Логи Nginx: sudo tail -f /var/log/nginx/error.log"
echo
echo "Приложение доступно по адресу: https://$DOMAIN"