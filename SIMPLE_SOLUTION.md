# Простое решение: Telegram Mini App на вашем домене

## У вас есть домен? Отлично! Вот что нужно сделать:

### Шаг 1: Получите VPS сервер
Арендуйте любой дешевый VPS:
- **Timeweb** (от 150₽/мес) - российский
- **REG.RU Cloud** (от 200₽/мес)  
- **DigitalOcean** (от $4/мес)
- **Vultr** (от $2.50/мес)

Минимальные требования:
- 1GB RAM
- 1 CPU
- Ubuntu 20.04+
- Статический IP

### Шаг 2: Настройте DNS
В панели управления вашим доменом создайте A-запись:
```
Тип: A
Имя: @ (для основного домена) или app (для поддомена)
Значение: IP-адрес_вашего_сервера
TTL: 3600
```

**Пример для разных регистраторов:**

**REG.RU:**
1. Войдите в личный кабинет
2. Выберите домен → DNS
3. Добавьте запись: A @ IP_СЕРВЕРА

**Namecheap:**
1. Domain List → Manage → Advanced DNS
2. Add New Record: A Record, Host: @, Value: IP_СЕРВЕРА

### Шаг 3: Разверните приложение одной командой
```bash
# Замените на ваш домен и данные сервера
./deploy.sh your-domain.com root@IP_СЕРВЕРА

# Пример
./deploy.sh myapp.com root@192.168.1.100
```

### Шаг 4: Настройте API ключи на сервере
```bash
# Подключитесь к серверу
ssh root@IP_СЕРВЕРА

# Отредактируйте конфигурацию
nano /home/webapp/telegram-mini-app/.env

# Добавьте ваши ключи:
TELEGRAM_BOT_TOKEN=ваш_токен_бота
YANDEX_API_KEY=ваш_ключ_yandex
YANDEX_FOLDER_ID=ваш_folder_id

# Перезапустите приложение
systemctl restart telegram-mini-app
```

### Шаг 5: Настройте бота в @BotFather
1. Откройте @BotFather в Telegram
2. Выберите вашего бота
3. Bot Settings → Menu Button → Configure Menu Button
4. Установите URL: `https://your-domain.com`

## Готово! 🎉

Теперь ваш Telegram Mini App доступен по адресу `https://your-domain.com` с:
- ✅ SSL сертификатом (автоматически)
- ✅ Автозапуском при перезагрузке
- ✅ Собственным доменом
- ✅ Высокой скоростью работы

## Полезные команды для сервера

**Проверить статус:**
```bash
systemctl status telegram-mini-app
```

**Посмотреть логи:**
```bash
journalctl -u telegram-mini-app -f
```

**Перезапустить:**
```bash
systemctl restart telegram-mini-app
```

## Стоимость решения
- Домен: уже есть у вас ✅
- VPS: от 150₽/месяц
- SSL: бесплатно (Let's Encrypt)
- **Итого: ~150₽/месяц**

Это профессиональное решение вместо ngrok!