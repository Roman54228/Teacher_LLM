# Интеграция с Telegram Mini App

## Шаг 1: Создание Telegram бота

### 1.1 Найдите @BotFather в Telegram
- Откройте Telegram
- Найдите пользователя **@BotFather**
- Начните диалог

### 1.2 Создайте нового бота
Отправьте команды по порядку:

```
/newbot
```

Введите имя бота (например):
```
Interview Prep Bot
```

Введите username бота (должен заканчиваться на 'bot'):
```
interview_prep_test_bot
```

### 1.3 Сохраните токен
BotFather даст вам токен вида:
```
1234567890:AABCdEfGhIjKlMnOpQrStUvWxYz
```

**Скопируйте этот токен!**

## Шаг 2: Настройка config.yaml

Откройте файл `config.yaml` и замените:

```yaml
telegram:
  bot_token: "1234567890:AABCdEfGhIjKlMnOpQrStUvWxYz"  # ВАШ ТОКЕН ЗДЕСЬ
  web_app_url: "http://localhost:5000"  # пока локально
```

## Шаг 3: Запуск локального тестирования

### 3.1 Запустите основное приложение
```bash
python telegram_app.py
```
Должно показать: `Running on http://127.0.0.1:5000`

### 3.2 Запустите простого бота
```bash
python telegram_bot_simple.py
```

Должно показать:
```
✓ Bot запущен и готов к работе!
💬 Попробуйте команду /start в Telegram
```

### 3.3 Проверьте в Telegram
1. Найдите своего бота по username
2. Отправьте `/start`
3. Должны появиться кнопки
4. Кнопка "О боте" должна работать

## Шаг 4: Настройка Mini App (требует ngrok)

### 4.1 Установите ngrok
- Скачайте с https://ngrok.com/
- Зарегистрируйтесь и получите authtoken

### 4.2 Запустите ngrok
```bash
ngrok http 5000
```

Скопируйте HTTPS URL (например):
```
https://abc123.ngrok.io
```

### 4.3 Обновите config.yaml
```yaml
telegram:
  bot_token: "ваш_токен"
  web_app_url: "https://abc123.ngrok.io"  # URL от ngrok
```

### 4.4 Настройте Menu Button в @BotFather

Отправьте BotFather:
```
/mybots
```

Выберите своего бота → `Bot Settings` → `Menu Button`

- Выберите `Configure menu button`
- **URL**: `https://abc123.ngrok.io` (ваш ngrok URL)
- **Text**: `🎯 Начать тест`

### 4.5 Перезапустите бота
```bash
python telegram_bot_simple.py
```

## Шаг 5: Тестирование Mini App

1. Откройте своего бота в Telegram
2. Найдите кнопку меню (справа от поля ввода)
3. Нажмите на неё - должно открыться приложение внутри Telegram
4. Попробуйте пройти тест

## Возможные проблемы

### Бот не отвечает:
- Проверьте токен в config.yaml
- Убедитесь что бот запущен
- Проверьте интернет

### Mini App не открывается:
- Используйте HTTPS URL (ngrok)
- Проверьте что localhost:5000 работает
- Убедитесь что URL в @BotFather правильный

### Ошибки в ngrok:
- Проверьте что порт 5000 свободен
- Перезапустите ngrok и обновите URL в config.yaml

## Альтернатива без ngrok

Если ngrok не работает, можно тестировать только кнопки бота:
1. Запустите `python telegram_bot_simple.py`
2. В Telegram отправьте `/start`
3. Кнопки "О боте" и "Статистика" будут работать
4. Mini App настроите позже

## Готовые команды для копирования

**Запуск всех компонентов:**
```bash
# Терминал 1 - основное приложение
python telegram_app.py

# Терминал 2 - простой бот  
python telegram_bot_simple.py

# Терминал 3 - ngrok (если нужен Mini App)
ngrok http 5000
```