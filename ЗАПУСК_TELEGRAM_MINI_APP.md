# Запуск Telegram Mini App - Пошаговая инструкция

## 1. Запуск приложения в Replit

### Шаг 1: Убедитесь что приложение запущено
```bash
# Приложение уже запущено через workflow "Telegram Mini App"
# Оно доступно по адресу: https://YOUR_REPLIT_ID.replit.app
```

### Шаг 2: Получите публичный URL
Ваше приложение доступно по адресу:
- **Внутренний URL**: `https://YOUR_REPLIT_ID.replit.app`
- **Порт**: 5000

## 2. Создание Telegram бота

### Шаг 1: Создайте бота через @BotFather
1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "Interview Prep Bot")
4. Введите username бота (например: "interview_prep_test_bot")
5. Получите **BOT_TOKEN**

### Шаг 2: Настройка Mini App
1. Отправьте @BotFather команду `/newapp`
2. Выберите созданного бота
3. Введите название приложения
4. Введите описание
5. Загрузите иконку 512x512px
6. **ВАЖНО**: Введите Web App URL: `https://YOUR_REPLIT_ID.replit.app`

## 3. Настройка в коде

### Обновите config.yaml
```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN_HERE"
  webhook_url: "https://YOUR_REPLIT_ID.replit.app"
```

### Запустите простой бот
```bash
# В терминале Replit:
python telegram_bot_simple.py
```

## 4. Тестирование

### Шаг 1: Найдите своего бота в Telegram
- Найдите бота по username (@interview_prep_test_bot)
- Отправьте команду `/start`

### Шаг 2: Запустите Mini App
- Нажмите кнопку "Открыть приложение" в боте
- Приложение должно открыться в Telegram

## 5. Альтернативный метод через localhost.run

Если у вас проблемы с прямым доступом к Replit:

### Запустите туннель
```bash
python setup_localhost_run.py
```

### Получите публичный URL
Скрипт выдаст URL вида: `https://abc123.localhost.run`

### Обновите настройки бота
Используйте полученный URL в настройках @BotFather для Web App

## 6. Проблемы и решения

### Проблема: "This site can't be reached"
**Решение**: Убедитесь что Replit приложение запущено и доступно

### Проблема: "Mini App не загружается"
**Решение**: 
1. Проверьте URL в настройках бота
2. Убедитесь что URL доступен в браузере
3. Проверьте что порт 5000 используется

### Проблема: "Telegram не открывает приложение"
**Решение**:
1. URL должен быть HTTPS
2. Проверьте что домен доступен извне
3. Попробуйте использовать localhost.run туннель

## 7. Быстрый старт

```bash
# 1. Убедитесь что workflow "Telegram Mini App" запущен
# 2. Получите ваш Replit URL
# 3. Создайте бота через @BotFather
# 4. Настройте Mini App с вашим URL
# 5. Протестируйте в Telegram
```

## Контакты
Если возникают проблемы - проверьте логи workflow в Replit консоли.