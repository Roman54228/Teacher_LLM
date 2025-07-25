# Быстрое развертывание на собственном домене

## Вариант 1: Автоматическое развертывание (рекомендуется)

### Подготовка
1. Купите домен (например, на reg.ru, namecheap.com)
2. Арендуйте VPS (например, на timeweb.ru, reg.ru, digitalocean.com)
3. Направьте домен на IP вашего сервера через DNS

### Быстрый запуск

**Для локального тестирования:**
```bash
# Локальное развертывание
./deploy.sh localhost
```

**Для развертывания на сервере:**
```bash
# Запустите скрипт развертывания на сервер
./deploy.sh your-domain.com webapp@your-server-ip

# Пример
./deploy.sh myapp.com webapp@192.168.1.100
```

### После автоматической установки

**Для локального тестирования:**
1. Отредактируйте файл `.env` в текущей папке
2. Добавьте ваши API ключи
3. Запустите: `source venv/bin/activate && python production_app.py`

**Для сервера:**
1. Подключитесь к серверу
2. Отредактируйте конфиг:
```bash
nano /home/webapp/telegram-mini-app/.env
```
3. Добавьте ваши ключи:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz
YANDEX_API_KEY=AQVNxxxxx...
YANDEX_FOLDER_ID=b1gxxxxx...
```
4. Перезапустите приложение:
```bash
sudo systemctl restart telegram-mini-app
```

## Вариант 2: Ручная установка

Следуйте подробному руководству в `PRODUCTION_DEPLOYMENT_GUIDE.md`

## Настройка Telegram Bot

1. Откройте @BotFather
2. Выберите вашего бота
3. Bot Settings → Menu Button → Configure Menu Button  
4. Установите URL: `https://your-domain.com`

## Проверка работы

1. Откройте `https://your-domain.com` в браузере
2. Убедитесь, что SSL работает (зеленый замочек)
3. Запустите бота в Telegram
4. Откройте Mini App через меню бота

## Полезные команды

### Проверка статуса
```bash
sudo systemctl status telegram-mini-app
sudo systemctl status nginx
```

### Просмотр логов
```bash
# Логи приложения
sudo journalctl -u telegram-mini-app -f

# Логи веб-сервера
sudo tail -f /var/log/nginx/error.log
```

### Обновление приложения
```bash
# Остановите сервис
sudo systemctl stop telegram-mini-app

# Обновите код в /home/webapp/telegram-mini-app/
# Затем запустите
sudo systemctl start telegram-mini-app
```

## Рекомендуемые провайдеры

### Домены (от 300₽/год)
- REG.RU
- Namecheap
- GoDaddy

### VPS серверы (от 200₽/месяц)
- Timeweb (российский)
- REG.RU Cloud
- DigitalOcean
- Vultr

## Минимальные требования сервера
- 1GB RAM
- 1 CPU Core  
- 10GB SSD
- Ubuntu 20.04+
- Статический IP

## Поддержка

После развертывания у вас будет полностью рабочий Telegram Mini App на собственном домене с SSL сертификатом и автозапуском.