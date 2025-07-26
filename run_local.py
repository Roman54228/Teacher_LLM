#!/usr/bin/env python3
"""
Простой скрипт для локального запуска Telegram Mini App
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Проверяем наличие необходимых зависимостей"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствуют зависимости: {e}")
        print("Установите зависимости: pip install -r requirements-production.txt")
        return False

def check_database():
    """Проверяем наличие базы данных"""
    db_file = Path("interview_prep.db")
    if db_file.exists():
        print("✅ База данных найдена")
        return True
    else:
        print("⚠️  База данных не найдена, будет создана автоматически")
        return False

def run_app():
    """Запускаем приложение"""
    print("🚀 Запуск Telegram Mini App...")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        return False
    
    # Проверяем базу данных
    check_database()
    
    print("\n📱 Приложение будет доступно по адресам:")
    print("   • Основное приложение: http://localhost:5000")
    print("   • API документация: http://localhost:5000/docs")
    print("   • ReDoc документация: http://localhost:5000/redoc")
    print("   • Health check: http://localhost:5000/health")
    
    print("\n🔄 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        # Запускаем приложение
        subprocess.run([
            sys.executable, "main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Приложение остановлено")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка запуска: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    print("🎯 Telegram Mini App - Локальный запуск")
    print("=======================================")
    
    # Проверяем что мы в правильной директории
    if not Path("main.py").exists():
        print("❌ Файл main.py не найден!")
        print("Запускайте скрипт в папке с кодом приложения")
        return False
    
    # Запускаем приложение
    return run_app()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 