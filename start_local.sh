#!/bin/bash
# Быстрый запуск Telegram Mini App для локальной разработки

echo "🚀 Быстрый запуск Telegram Mini App"
echo "==================================="

# Проверяем что мы в правильной папке
if [ ! -f "main.py" ]; then
    echo "❌ Файл main.py не найден!"
    echo "Запускайте скрипт в папке с кодом приложения"
    exit 1
fi

# Проверяем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем зависимости если нужно
if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    echo "📦 Установка зависимостей..."
    pip install -r requirements-production.txt
fi

echo "✅ Все готово!"
echo
echo "📱 Приложение будет доступно по адресам:"
echo "   • Основное приложение: http://localhost:5000"
echo "   • API документация: http://localhost:5000/docs"
echo "   • ReDoc документация: http://localhost:5000/redoc"
echo "   • Health check: http://localhost:5000/health"
echo
echo "🔄 Для остановки нажмите Ctrl+C"
echo "=" * 50

# Запускаем приложение
python main.py 