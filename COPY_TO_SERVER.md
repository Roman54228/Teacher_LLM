# 🚀 Инструкция по копированию файлов на сервер

## Проблема
На сервере filonov.space старая версия кода, поэтому появляется ошибка `SyntaxError: Unexpected token '<'`.

## Файлы для копирования

Скопируйте эти 4 файла с Replit на сервер filonov.space:

### 1. `templates/index.html`
**Что исправлено:**
- Строка 5054: `window.userAnswers[questionId]?.correct` (было `is_correct`)
- Строки 5855-5856: `module.emoji || module.icon || '📚'` и `module.name || 'Модуль'`
- Исправлена обработка API данных модулей

### 2. `production_app.py`
**Что исправлено:**
- Строки 219-222: правильный вызов `get_questions_by_subcategory(category, subcategory)`
- Добавлены все API роуты: `/api/modules`, `/api/questions/<category>`, `/api/progress`
- Исправлены импорты YandexGPTHelper

### 3. `utils/database.py`
**Что исправлено:**
- Строки 231, 235: добавлено `sub_category=q_data.get('sub_category')` для корректного сохранения подкатегорий
- Исправлен метод `load_questions_to_db` для обработки подкатегорий

### 4. `utils/yandex_gpt_helper.py`
**Что добавлено:**
- Полный класс `YandexGPTHelper` для работы с YandexGPT API

## Команды на сервере

После копирования файлов выполните:

```bash
# Перезагрузите данные в базу
cd /path/to/telegram-mini-app
python3 load_screening_questions.py
python3 load_python_questions.py

# Перезапустите приложение
systemctl restart telegram-mini-app

# Проверьте статус
systemctl status telegram-mini-app
```

## Проверка работы

После перезапуска проверьте:

1. **API модулей:** `curl http://localhost:5000/api/modules`
2. **Скрининговые вопросы:** `curl "http://localhost:5000/api/questions/Screening%20Test?subcategory=Тест"`
3. **Python вопросы:** `curl "http://localhost:5000/api/questions/Python?subcategory=Основы%20Python"`

Все должно вернуть JSON данные, а не HTML ошибки.

## Ожидаемый результат

После копирования файлов:
- ✅ Исчезнет ошибка `SyntaxError: Unexpected token '<'`
- ✅ Модули будут отображаться с иконками
- ✅ В тестах появятся вопросы (15 скрининговых, 15 Python)  
- ✅ Социальное сравнение покажет правильные результаты