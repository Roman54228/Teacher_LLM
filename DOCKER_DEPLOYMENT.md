# Docker развертывание Telegram Mini App

## Быстрый старт

### 1. Подготовка на сервере

```bash
# Скопируйте папку с кодом на сервер любым способом:
# - scp -r ./telegram-mini-app user@server:/home/user/
# - rsync -avz ./telegram-mini-app user@server:/home/user/
# - git clone (если код в репозитории)

# Перейдите в папку проекта
cd telegram-mini-app
```

### 2. Запуск интерактивного режима

```bash
# Запустите скрипт настройки
./docker-setup.sh

# Выберите "1" для интерактивного режима
# Вы попадете в bash контейнера
```

### 3. Внутри Docker контейнера

```bash
# Вы окажетесь внутри контейнера в /app директории
# Все файлы проекта доступны

# Отредактируйте .env файл (добавьте API ключи)
nano .env

# Запустите приложение вручную
python production_app.py

# Или в фоновом режиме
nohup python production_app.py &

# Проверьте что приложение работает
curl http://localhost:5000
```

## Режимы работы

### Интерактивный режим
- Запускает контейнер с bash
- Вы можете входить и выходить
- Полный контроль над процессами

```bash
./docker-setup.sh
# Выберите: 1) Интерактивный режим
```

### Автоматический режим  
- Приложение запускается автоматически
- Работает в фоне как сервис
- Автоперезапуск при сбоях

```bash
./docker-setup.sh  
# Выберите: 2) Автоматический режим
```

## Полезные команды

### Работа с контейнерами
```bash
# Посмотреть статус
docker-compose ps

# Войти в работающий контейнер
docker exec -it telegram-mini-app-server bash

# Посмотреть логи
docker-compose logs -f app

# Перезапустить
docker-compose restart app

# Остановить все
docker-compose down
```

### Внутри контейнера
```bash
# Проверить процессы
ps aux

# Проверить порты
netstat -tlnp

# Проверить логи приложения
tail -f logs/telegram_mini_app.log

# Перезапустить приложение
pkill -f python
python production_app.py &
```

## Настройка Nginx (на хосте)

Если хотите использовать домен, настройте Nginx на хост-системе:

```nginx
# /etc/nginx/sites-available/telegram-mini-app
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активировать конфигурацию
sudo ln -s /etc/nginx/sites-available/telegram-mini-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Получить SSL сертификат
sudo certbot --nginx -d your-domain.com
```

## Структура проекта в Docker

```
/app/
├── telegram_app.py      # Основное приложение
├── production_app.py    # Production версия
├── templates/           # HTML шаблоны
├── utils/              # Утилиты
├── data/               # Данные (маунтится как том)
├── logs/               # Логи (маунтится как том)
├── .env                # Конфигурация
└── ...
```

## Преимущества Docker решения

✅ **Изолированная среда** - не влияет на хост-систему  
✅ **Воспроизводимость** - одинаково работает везде  
✅ **Простое развертывание** - один скрипт для всего  
✅ **Интерактивный доступ** - можете войти в контейнер  
✅ **Автоматические перезапуски** - при сбоях  
✅ **Простое обновление** - пересборка образа  

## Обновление приложения

```bash
# Остановить контейнеры
docker-compose down

# Обновить код (загрузить новые файлы)

# Пересобрать образ
docker-compose build

# Запустить заново
./docker-setup.sh
```

## Мониторинг

```bash
# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f

# Проверка здоровья
curl http://localhost:5000/api/progress
```

Теперь у вас есть полноценное Docker решение с интерактивным доступом!