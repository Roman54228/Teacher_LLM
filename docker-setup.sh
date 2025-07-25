#!/bin/bash
# Скрипт для настройки и запуска Telegram Mini App в Docker

set -e

echo "🐳 Настройка Docker для Telegram Mini App"
echo "========================================="

# Функция проверки Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker не установлен!"
        echo "Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose не установлен!"
        echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo "✅ Docker установлен"
}

# Создание .env файла если не существует
create_env_file() {
    if [ ! -f .env ]; then
        echo "📝 Создание .env файла..."
        cat > .env << 'EOF'
# Telegram Bot (ЗАПОЛНИТЕ СВОИ ДАННЫЕ)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# YandexGPT API (ЗАПОЛНИТЕ СВОИ ДАННЫЕ)
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id

# Database
DATABASE_URL=sqlite:///data/interview_prep.db

# Production settings
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Domain (замените на ваш домен)
DOMAIN=localhost
EOF
        echo "✅ Файл .env создан"
        echo "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваши API ключи!"
    else
        echo "✅ Файл .env уже существует"
    fi
}

# Создание необходимых директорий
create_directories() {
    echo "📁 Создание директорий..."
    mkdir -p data logs static
    echo "✅ Директории созданы"
}

# Функция для интерактивного режима
interactive_mode() {
    echo "🔧 Запуск в интерактивном режиме..."
    echo "Вы сможете войти в контейнер и управлять им вручную"
    
    # Остановка существующих контейнеров
    docker-compose down 2>/dev/null || true
    
    # Сборка образа
    echo "🏗️  Сборка Docker образа..."
    docker-compose build
    
    # Запуск интерактивного контейнера
    echo "🚀 Запуск интерактивного контейнера..."
    docker-compose run --rm --service-ports telegram-mini-app
}

# Функция для автоматического режима
auto_mode() {
    echo "🤖 Запуск в автоматическом режиме..."
    
    # Остановка существующих контейнеров
    docker-compose down 2>/dev/null || true
    
    # Сборка образа
    echo "🏗️  Сборка Docker образа..."
    docker-compose build
    
    # Запуск приложения
    echo "🚀 Запуск приложения..."
    docker-compose up -d app
    
    echo "✅ Приложение запущено!"
    echo "📱 Доступно по адресу: http://localhost:5000"
    echo
    echo "Полезные команды:"
    echo "  docker-compose logs -f app     # Просмотр логов"
    echo "  docker-compose stop           # Остановка"
    echo "  docker-compose restart app    # Перезапуск"
    echo "  docker exec -it telegram-mini-app-server bash  # Вход в контейнер"
}

# Главная функция
main() {
    check_docker
    create_directories
    create_env_file
    
    echo
    echo "Выберите режим запуска:"
    echo "1) Интерактивный режим (вы войдете в bash контейнера)"
    echo "2) Автоматический режим (приложение запустится автоматически)"
    echo "3) Остановить все контейнеры"
    echo "4) Показать статус"
    echo
    
    read -p "Введите номер (1-4): " choice
    
    case $choice in
        1)
            interactive_mode
            ;;
        2)
            auto_mode
            ;;
        3)
            echo "⏹️  Остановка контейнеров..."
            docker-compose down
            echo "✅ Контейнеры остановлены"
            ;;
        4)
            echo "📊 Статус контейнеров:"
            docker-compose ps
            echo
            echo "📋 Логи приложения:"
            docker-compose logs --tail=20 app 2>/dev/null || echo "Контейнер не запущен"
            ;;
        *)
            echo "❌ Неверный выбор"
            exit 1
            ;;
    esac
}

# Запуск основной функции
main "$@"