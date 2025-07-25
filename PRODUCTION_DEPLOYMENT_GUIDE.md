# Руководство по развертыванию на собственном домене

## Обзор

Это руководство поможет вам развернуть Telegram Mini App на собственном сервере с доменным именем вместо ngrok.

## Требования

### 1. Сервер
- VPS/VDS с Ubuntu 20.04+ или аналогичная ОС
- Минимум 1GB RAM, 1 CPU
- Статический IP-адрес
- Доступ по SSH

### 2. Доменное имя
- Зарегистрированный домен (например, myapp.com)
- Доступ к DNS настройкам домена

### 3. SSL сертификат
- Let's Encrypt (бесплатный) или коммерческий SSL
- Telegram требует HTTPS для Mini Apps

## Шаг 1: Настройка сервера

### Подключение к серверу
```bash
ssh root@your-server-ip
# или
ssh username@your-server-ip
```

### Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### Установка необходимых пакетов
```bash
# Python и системные зависимости
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git -y

# Установка Node.js (если нужен)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Шаг 2: Настройка домена

### DNS записи
В панели управления доменом создайте A-запись:
```
Тип: A
Имя: @ (или www)
Значение: your-server-ip
TTL: 3600
```

Для поддомена (например, app.mydomain.com):
```
Тип: A
Имя: app
Значение: your-server-ip
TTL: 3600
```

### Проверка DNS
```bash
# Проверьте, что домен указывает на ваш сервер
dig your-domain.com
nslookup your-domain.com
```

## Шаг 3: Загрузка и настройка приложения

### Создание пользователя для приложения
```bash
sudo adduser webapp
sudo usermod -aG sudo webapp
su - webapp
```

### Клонирование кода
```bash
# Если у вас есть git репозиторий
git clone https://github.com/your-repo/telegram-mini-app.git
cd telegram-mini-app

# Или загрузите файлы через scp/rsync
```

### Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Настройка переменных окружения
```bash
# Создайте файл .env
nano .env
```

Содержимое .env файла:
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# YandexGPT API
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id

# Database
DATABASE_URL=sqlite:///interview_prep.db

# Production settings
FLASK_ENV=production
DEBUG=False

# Domain
DOMAIN=your-domain.com
```

## Шаг 4: Настройка Nginx

### Создание конфигурации Nginx
```bash
sudo nano /etc/nginx/sites-available/telegram-mini-app
```

Содержимое файла:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket поддержка (если нужна)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Статические файлы (если есть)
    location /static/ {
        alias /home/webapp/telegram-mini-app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Активация конфигурации
```bash
sudo ln -s /etc/nginx/sites-available/telegram-mini-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Шаг 5: Получение SSL сертификата

### Автоматическое получение Let's Encrypt
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Проверка автообновления
```bash
sudo certbot renew --dry-run
```

## Шаг 6: Настройка systemd сервиса

### Создание файла сервиса
```bash
sudo nano /etc/systemd/system/telegram-mini-app.service
```

Содержимое:
```ini
[Unit]
Description=Telegram Mini App
After=network.target

[Service]
Type=simple
User=webapp
WorkingDirectory=/home/webapp/telegram-mini-app
Environment=PATH=/home/webapp/telegram-mini-app/venv/bin
ExecStart=/home/webapp/telegram-mini-app/venv/bin/python telegram_app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-mini-app
sudo systemctl start telegram-mini-app
sudo systemctl status telegram-mini-app
```

## Шаг 7: Настройка Telegram Bot

### Обновление WebApp URL
Используйте BotFather для обновления URL вашего Mini App:

1. Откройте @BotFather в Telegram
2. Выберите /mybots
3. Выберите вашего бота
4. Bot Settings → Menu Button → Configure Menu Button
5. Установите URL: `https://your-domain.com`

### Установка Webhook (если используется)
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/webhook"}'
```

## Шаг 8: Настройка базы данных (Production)

### Для PostgreSQL (рекомендуется для production)
```bash
# Установка PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Создание базы данных
sudo -u postgres createuser --interactive
sudo -u postgres createdb telegram_mini_app

# Обновите DATABASE_URL в .env
DATABASE_URL=postgresql://username:password@localhost/telegram_mini_app
```

### Для SQLite (простой вариант)
```bash
# Убедитесь, что файл БД доступен для записи
sudo chown webapp:webapp /home/webapp/telegram-mini-app/interview_prep.db
sudo chmod 664 /home/webapp/telegram-mini-app/interview_prep.db
```

## Шаг 9: Мониторинг и логи

### Просмотр логов приложения
```bash
sudo journalctl -u telegram-mini-app -f
```

### Просмотр логов Nginx
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Мониторинг ресурсов
```bash
# Установка htop для мониторинга
sudo apt install htop -y
htop
```

## Шаг 10: Резервное копирование

### Автоматическое резервное копирование БД
```bash
# Создайте скрипт backup.sh
nano /home/webapp/backup.sh
```

Содержимое backup.sh:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/webapp/backups"
mkdir -p $BACKUP_DIR

# Backup SQLite
cp /home/webapp/telegram-mini-app/interview_prep.db $BACKUP_DIR/interview_prep_$DATE.db

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "interview_prep_*.db" -mtime +7 -delete
```

### Добавьте в crontab
```bash
chmod +x /home/webapp/backup.sh
crontab -e

# Добавьте строку для ежедневного бэкапа в 2:00
0 2 * * * /home/webapp/backup.sh
```

## Проверка развертывания

1. Откройте https://your-domain.com в браузере
2. Проверьте, что SSL работает (зеленый замочек)
3. Протестируйте Telegram Mini App
4. Проверьте логи на ошибки

## Устранение неполадок

### Проблемы с SSL
```bash
# Проверка сертификата
sudo certbot certificates

# Принудительное обновление
sudo certbot renew --force-renewal
```

### Проблемы с сервисом
```bash
# Перезапуск сервиса
sudo systemctl restart telegram-mini-app

# Проверка статуса
sudo systemctl status telegram-mini-app

# Просмотр логов
sudo journalctl -u telegram-mini-app --since "1 hour ago"
```

### Проблемы с Nginx
```bash
# Тест конфигурации
sudo nginx -t

# Перезагрузка
sudo systemctl reload nginx

# Проверка статуса
sudo systemctl status nginx
```

## Безопасность

### Настройка файрвола
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### Обновления безопасности
```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure unattended-upgrades
```

### Ограничение доступа к админке
```nginx
# В конфигурации Nginx добавьте для /admin
location /admin {
    allow your.home.ip.address;
    deny all;
    proxy_pass http://127.0.0.1:5001;
    # ... остальные proxy_set_header
}
```

## Поддержка

После развертывания у вас будет:
- ✅ Telegram Mini App на собственном домене
- ✅ HTTPS с автообновляемым SSL
- ✅ Автозапуск при перезагрузке сервера
- ✅ Централизованные логи
- ✅ Автоматические резервные копии
- ✅ Мониторинг и уведомления

Для получения помощи проверьте логи и обратитесь к документации компонентов.