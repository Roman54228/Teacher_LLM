# Быстрое исправление проблемы с подсчетом баллов

## Проблема:
Показывает 0/10 правильных ответов в социальном сравнении, хотя пользователь ответил правильно.

## Причина:
Ошибка в JavaScript коде - неправильное имя поля при подсчете правильных ответов.

## Исправление:

### Шаг 1: Обновите файлы на сервере

**Скопируйте эти 3 исправленных файла на сервер:**
1. `templates/index.html` (исправлена строка 5054) 
2. `production_app.py` (исправлены импорты и API методы)
3. `utils/yandex_gpt_helper.py` (добавлен класс YandexGPTHelper)

```bash
# На сервере:
ssh root@your-server-ip
cd /root/telegram-mini-app  # или где установлено ваше приложение
```

### Шаг 2: Перезапустите приложение
```bash
# Остановить текущее приложение
systemctl stop telegram-mini-app

# Перезапустить приложение  
systemctl restart telegram-mini-app

# Проверить статус
systemctl status telegram-mini-app
```

## Что исправлено:

### В файле `templates/index.html`:
**Строка 5054:** Исправлено поле для проверки правильных ответов
```javascript
// БЫЛО (неправильно):
window.userAnswers[questionId]?.is_correct

// СТАЛО (правильно):
window.userAnswers[questionId]?.correct  
```

**Строки 5250, 5323, 5778:** Исправлена обработка API данных модулей
```javascript
// БЫЛО (ошибка data.categories.map is not a function):
data.categories.map(...) 
data.modules.forEach(...)
module.submodules.forEach(...)

// СТАЛО (правильная обработка):
Array.isArray(data) ? data : (data.modules || [])
modules.forEach(...)
module.topics.forEach(...)
```

**Строки 5855, 5856:** Исправлено отображение иконок и названий модулей
```javascript
// БЫЛО (undefined иконки и названия):
module.icon
module.name

// СТАЛО (fallback для всех полей):
module.emoji || module.icon || '📚'
module.name || 'Модуль'
```

### В файле `production_app.py`:
1. **Исправлен ImportError** - убран неправильный импорт `DatabaseProgressTracker`
2. **Добавлены недостающие API роуты**: `/api/progress`, `/api/categories`
3. **Исправлен формат данных modules.json** - преобразование в ожидаемый фронтендом формат
4. **Добавлена обработка ошибок JSON** - приложение не падает при проблемах с данными

### В файле `utils/yandex_gpt_helper.py`:
1. **Добавлен класс YandexGPTHelper** - для совместимости с импортами
2. **Исправлена интеграция с YandexGPT API** - теперь AI помощник работает корректно

## Результат:
Теперь в социальном сравнении будет правильно показывать количество правильных ответов вместо 0/10.

---

## Дополнительно: Добавьте API ключи
```bash
nano .env
```

Добавьте в файл (замените на реальные значения):
```
TELEGRAM_BOT_TOKEN=123456789:ABC...your_real_token
YANDEX_API_KEY=your_real_api_key
YANDEX_FOLDER_ID=your_real_folder_id
DATABASE_URL=sqlite:///interview_prep.db
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

## Шаг 3: Перезапустите приложение
```bash
systemctl restart telegram-mini-app
systemctl status telegram-mini-app
```

## Шаг 4: Проверьте логи
```bash
journalctl -u telegram-mini-app -f
```

Должно появиться:
```
🚀 Starting Telegram Mini App in production mode...
✅ Server starting on 0.0.0.0:5000
```

## Шаг 5: Настройте SSL (по желанию)
```bash
certbot --nginx -d filonov.space -d www.filonov.space
```

## Готово!
Приложение работает на `http://filonov.space` (или `https://` если SSL настроен)

---

## Если не работает:

### Проверьте порт 5000:
```bash
netstat -tulpn | grep :5000
```

### Перезапустите Nginx:
```bash
systemctl restart nginx
```

### Проверьте диагностику:
```bash
systemctl status telegram-mini-app nginx
```