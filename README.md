# Interview Prep - Telegram Mini App

**FastAPI-powered** Telegram Mini App для подготовки к техническим собеседованиям с ИИ-поддержкой и админ-панелью.

## Архитектура

### ⚡ FastAPI Backend
- **Основное приложение**: `main.py` (порт 5002)
- **Админ-панель**: `admin_fastapi.py` (порт 5003)
- **Автодокументация**: `/docs` и `/redoc`
- **Async поддержка**: Высокая производительность
- **Type Safety**: Pydantic модели и type hints

## Установка и запуск локально

### 1. Требования
- Python 3.8+
- PostgreSQL или SQLite
- Telegram Bot Token
- YandexGPT API ключи

### 2. Клонирование и установка зависимостей

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd interview-prep-telegram

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Установите зависимости
pip install fastapi uvicorn python-telegram-bot pandas plotly psycopg2-binary requests sqlalchemy pydantic jinja2
```

### 3. Настройка PostgreSQL

```bash
# Установите PostgreSQL и создайте базу данных
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
# или
brew install postgresql  # macOS

# Создайте базу данных
sudo -u postgres createdb interview_prep

# Создайте пользователя
sudo -u postgres psql
CREATE USER interview_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE interview_prep TO interview_user;
\q
```

### 4. Переменные окружения

Создайте файл `.env` в корне проекта:

```bash
# База данных
DATABASE_URL=postgresql://interview_user:your_password@localhost:5432/interview_prep
PGHOST=localhost
PGPORT=5432
PGDATABASE=interview_prep
PGUSER=interview_user
PGPASSWORD=your_password

# YandexGPT API
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
WEB_APP_URL=https://your-domain.com  # или ngrok URL для тестирования

# Админ панель
ADMIN_PASSWORD=admin123
ADMIN_SECRET_KEY=your-secret-key
```

### 5. Получение API ключей

#### YandexGPT:
1. Зайдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте сервисный аккаунт
3. Получите API ключ и ID папки

#### Telegram Bot:
1. Напишите @BotFather в Telegram
2. Используйте команду `/newbot`
3. Следуйте инструкциям и получите токен

### 6. Инициализация базы данных

```bash
# Загрузите переменные окружения
export $(cat .env | xargs)

# Создайте таблицы и загрузите вопросы
python -c "
from utils.database import db_manager
import json

# Создание таблиц
db_manager.create_tables()
print('Таблицы созданы')

# Загрузка вопросов
try:
    with open('data/questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    db_manager.load_questions_to_db(questions_data)
    print('Вопросы загружены')
except Exception as e:
    print(f'Ошибка загрузки вопросов: {e}')
"
```

### 7. Запуск приложений

#### FastAPI Applications:

**Основное приложение (Telegram Mini App):**
```bash
python main.py
# или с uvicorn
uvicorn main:app --host 0.0.0.0 --port 5002 --reload
```

**Админ-панель:**
```bash
python admin_fastapi.py
# или с uvicorn  
uvicorn admin_fastapi:app --host 0.0.0.0 --port 5003 --reload
```

#### Доступ к приложениям:
- **Основное приложение**: http://localhost:5002
- **Админ-панель**: http://localhost:5003
- **API документация**: http://localhost:5002/docs
- **Redoc документация**: http://localhost:5002/redoc

### 8. Настройка для локального тестирования с Telegram

Для тестирования с реальным Telegram используйте ngrok:

```bash
# Установите ngrok
# Скачайте с https://ngrok.com/

# Запустите туннель для основного приложения
ngrok http 5002

# Скопируйте HTTPS URL (например: https://abc123.ngrok.io)
# Обновите WEB_APP_URL в .env файле
```

Затем настройте Web App в @BotFather:
1. `/mybots` → выберите своего бота
2. `Bot Settings` → `Menu Button` → `Configure Menu Button`
3. Укажите ваш ngrok URL

### 9. Структура проекта

```
interview-prep-telegram/
├── main.py                  # Основное FastAPI приложение (АКТИВНОЕ)
├── admin_fastapi.py         # FastAPI админ-панель (АКТИВНОЕ)
├── telegram_bot.py          # Telegram бот
├── *_OLD.py                 # Устаревшие Flask/Streamlit файлы (НЕ ИСПОЛЬЗУЮТСЯ)
├── utils/
│   ├── database.py          # Работа с БД
│   ├── db_progress_tracker.py  # Отслеживание прогресса
│   └── yandex_gpt_helper.py    # YandexGPT интеграция
├── templates/               # HTML шаблоны
│   ├── index.html          # Основной интерфейс
│   ├── admin_login.html    # Вход в админку
│   ├── admin_dashboard.html # Дашборд админки
│   ├── admin_category.html # Управление категорией
│   ├── admin_question.html # Редактирование вопроса
│   └── admin_new_question.html # Новый вопрос
├── data/
│   └── questions.json      # Начальные вопросы
├── .env                    # Переменные окружения
└── README.md              # Эта инструкция
```

### 10. Использование

#### Для пользователей:
1. Найдите ваш бот в Telegram
2. Нажмите `/start`
3. Нажмите кнопку меню для запуска Mini App

#### Для администраторов:
1. Откройте http://localhost:5001/admin
2. Введите пароль (по умолчанию: admin123)
3. Управляйте вопросами, добавляйте подсказки
4. Отмечайте вопросы как проверенные

### 11. Возможные проблемы

#### Ошибки базы данных:
```bash
# Проверьте подключение к PostgreSQL
psql -h localhost -U interview_user -d interview_prep

# Пересоздайте таблицы если нужно
python -c "from utils.database import db_manager; db_manager.create_tables()"
```

#### Ошибки YandexGPT:
- Проверьте правильность API ключа и folder_id
- Убедитесь что у сервисного аккаунта есть права на YandexGPT

#### Telegram не открывает приложение:
- Проверьте что WEB_APP_URL доступен извне (используйте ngrok)
- Убедитесь что URL настроен в @BotFather

### 12. Production деплой

Для продакшн деплоя:
1. Используйте uvicorn для production вместо dev режима
2. Настройте nginx как reverse proxy
3. Используйте systemd для автозапуска
4. Настройте SSL сертификат (обязательно для Telegram)

```bash
# Пример запуска с gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 telegram_app:app
gunicorn -w 2 -b 0.0.0.0:5001 admin:app
```