# Решение проблем после развертывания

## Проблема 1: Приложение не запускается (код ошибки 1)

**Причина:** Отсутствуют API ключи для YandexGPT

**Решение:**
```bash
# Подключитесь к серверу
ssh root@your-server-ip

# Отредактируйте конфигурацию
nano /home/webapp/telegram-mini-app/.env

# Добавьте ваши ключи (замените на реальные):
TELEGRAM_BOT_TOKEN=123456789:ABCdef...your_bot_token
YANDEX_API_KEY=your_yandex_api_key  
YANDEX_FOLDER_ID=your_yandex_folder_id

# Сохраните файл (Ctrl+X, Y, Enter)

# Перезапустите приложение
systemctl restart telegram-mini-app

# Проверьте статус
systemctl status telegram-mini-app
```

## Проблема 2: SSL сертификат не получается

**Причина:** DNS не настроен или домен недоступен

**Решение:**

### Шаг 1: Проверьте DNS
```bash
# Проверьте что домен указывает на ваш сервер
dig your-domain.com A
nslookup your-domain.com
```

### Шаг 2: Настройте DNS у регистратора домена
- Добавьте A-запись: `your-domain.com` → `IP_сервера`
- Добавьте A-запись: `www.your-domain.com` → `IP_сервера`

### Шаг 3: Подождите и повторите SSL
```bash
# Подождите 5-10 минут для распространения DNS
# Затем повторите получение SSL
certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Проблема 3: Проверка статуса приложения

```bash
# Статус сервиса
systemctl status telegram-mini-app

# Логи приложения (последние строки)
journalctl -u telegram-mini-app -n 50

# Логи в реальном времени
journalctl -u telegram-mini-app -f

# Статус Nginx
systemctl status nginx

# Проверка конфигурации Nginx
nginx -t
```

## Проблема 4: Приложение запускается, но недоступно через браузер

**Решение:**
```bash
# Проверьте что приложение слушает порт 5000
netstat -tulpn | grep :5000

# Проверьте файрвол
ufw status

# Проверьте Nginx
curl http://localhost:5000
curl http://your-domain.com
```

## Быстрая диагностика

```bash
# Запустите эту команду для полной диагностики:
echo "=== Диагностика системы ===" && \
systemctl status telegram-mini-app --no-pager && \
echo -e "\n=== Nginx статус ===" && \
systemctl status nginx --no-pager && \
echo -e "\n=== Порты ===" && \
netstat -tulpn | grep -E ':(80|443|5000)' && \
echo -e "\n=== Последние логи ===" && \
journalctl -u telegram-mini-app -n 10 --no-pager
```

## Полный перезапуск

Если ничего не помогает:
```bash
# Остановите всё
systemctl stop telegram-mini-app
systemctl stop nginx

# Перезапустите с нуля
systemctl start nginx
systemctl start telegram-mini-app

# Проверьте статус
systemctl status telegram-mini-app
systemctl status nginx
```

## Контакты для поддержки

Если проблемы остаются:
1. Скопируйте вывод команды диагностики выше
2. Приложите содержимое файла `.env` (без API ключей!)
3. Укажите ваш домен и IP сервера