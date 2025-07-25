# Развертывание на сервере (пошаговая инструкция)

## Шаг 1: Скопируйте код на сервер

```bash
# На вашем компьютере - создайте архив
tar -czf telegram-mini-app.tar.gz * 

# Скопируйте на сервер
scp telegram-mini-app.tar.gz root@your-server-ip:/root/

# Или используйте любой другой способ (git, rsync, etc.)
```

## Шаг 2: Подключитесь к серверу

```bash
ssh root@your-server-ip
```

## Шаг 3: Распакуйте и разверните

```bash
# Создайте папку и распакуйте
mkdir telegram-mini-app
cd telegram-mini-app
tar -xzf ../telegram-mini-app.tar.gz

# Запустите скрипт развертывания
./server-deploy.sh
```

Скрипт спросит ваш домен и автоматически:
- Установит все зависимости
- Настроит Nginx
- Получит SSL сертификат  
- Запустит приложение как сервис

## Шаг 4: Настройте DNS домена

**ВАЖНО:** Перед настройкой API ключей убедитесь что DNS настроен правильно!

1. **В панели вашего регистратора домена** добавьте записи:
   - A-запись: `filonov.space` → `IP_вашего_сервера`
   - A-запись: `www.filonov.space` → `IP_вашего_сервера`

2. **Подождите 5-10 минут** для распространения DNS

3. **Проверьте DNS**:
```bash
dig filonov.space A
```

## Шаг 5: Добавьте API ключи

```bash
# Отредактируйте конфигурацию
nano /home/webapp/telegram-mini-app/.env

# Добавьте ваши ключи:
TELEGRAM_BOT_TOKEN=ваш_токен_бота
YANDEX_API_KEY=ваш_ключ_yandex
YANDEX_FOLDER_ID=ваш_folder_id

# Перезапустите приложение
systemctl restart telegram-mini-app
```

## Шаг 6: Получите SSL сертификат

```bash
# После настройки DNS и API ключей:
certbot --nginx -d filonov.space -d www.filonov.space
```

## Шаг 7: Настройте @BotFather

1. Откройте @BotFather в Telegram
2. Выберите вашего бота
3. Bot Settings → Menu Button → Configure Menu Button
4. Установите URL: `https://filonov.space`

## Готово! 🎉

Приложение работает на `https://your-domain.com`

## Полезные команды

```bash
# Проверить статус
systemctl status telegram-mini-app

# Посмотреть логи
journalctl -u telegram-mini-app -f

# Перезапустить
systemctl restart telegram-mini-app

# Остановить
systemctl stop telegram-mini-app
```

---

**Что делает server-deploy.sh:**
- ✅ Устанавливает Python, Nginx, Certbot
- ✅ Создает пользователя webapp  
- ✅ Настраивает виртуальное окружение
- ✅ Устанавливает зависимости
- ✅ Создает systemd сервис
- ✅ Настраивает Nginx с SSL
- ✅ Запускает приложение

**Результат:** Полностью рабочий Telegram Mini App на вашем домене