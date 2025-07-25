#!/usr/bin/env python3
"""
Быстрая настройка Telegram Mini App
"""

import os
import time
import subprocess
import threading
import sys
from pathlib import Path

def show_setup_instructions():
    """Показывает инструкции по настройке"""
    print("\n" + "="*60)
    print("📱 БЫСТРАЯ НАСТРОЙКА TELEGRAM MINI APP")
    print("="*60)
    
    print("\n🎯 ШАГ 1: Создание бота в Telegram")
    print("   1. Откройте Telegram и найдите @BotFather")
    print("   2. Отправьте команду: /newbot")
    print("   3. Введите имя бота: Interview Prep Bot")
    print("   4. Введите username: interview_prep_test_bot")
    print("   5. Скопируйте токен бота")
    
    print("\n🔧 ШАГ 2: Настройка токена")
    print("   1. Откройте файл config.yaml")
    print("   2. Найдите строку с 'ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ'")
    print("   3. Замените на ваш токен")
    
    print("\n🌐 ШАГ 3: Создание публичного URL")
    print("   Варианты:")
    print("   A) Используйте ngrok:")
    print("      • Установите ngrok с https://ngrok.com")
    print("      • Запустите: ngrok http 5000")
    print("      • Скопируйте https URL")
    print("   B) Используйте локальный туннель:")
    print("      • Запустите: python tunnel_fix.py")
    print("      • Скопируйте URL из вывода")
    
    print("\n📲 ШАГ 4: Настройка Mini App")
    print("   1. Напишите @BotFather")
    print("   2. Отправьте: /mybots")
    print("   3. Выберите своего бота")
    print("   4. Bot Settings > Menu Button")
    print("   5. Configure menu button")
    print("   6. URL: ваш публичный URL")
    print("   7. Text: 🎯 Начать тест")
    
    print("\n✅ ШАГ 5: Тестирование")
    print("   1. Найдите бота в Telegram")
    print("   2. Отправьте /start")
    print("   3. Нажмите кнопку меню")
    print("   4. Должно открыться приложение")
    
    print("\n" + "="*60)
    print("🚀 ГОТОВО! Ваш Telegram Mini App настроен")
    print("="*60)

def check_app_status():
    """Проверяет статус приложения"""
    print("\n📊 Проверка статуса приложения...")
    
    # Проверяем основное приложение
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Основное приложение работает (порт 5000)")
        else:
            print(f"⚠️ Основное приложение отвечает с кодом {response.status_code}")
    except Exception as e:
        print(f"❌ Основное приложение недоступно: {e}")
    
    # Проверяем админ панель
    try:
        import requests
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print("✅ Админ панель работает (порт 5001)")
        else:
            print(f"⚠️ Админ панель отвечает с кодом {response.status_code}")
    except Exception as e:
        print(f"❌ Админ панель недоступна: {e}")

def check_config():
    """Проверяет конфигурацию"""
    print("\n⚙️ Проверка конфигурации...")
    
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ Файл config.yaml не найден")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ" in content:
            print("⚠️ Токен бота не настроен в config.yaml")
            return False
        elif "your_telegram_bot_token_here" in content:
            print("⚠️ Токен бота не настроен в config.yaml")
            return False
        else:
            print("✅ Конфигурация выглядит настроенной")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при чтении config.yaml: {e}")
        return False

def suggest_next_steps():
    """Предлагает следующие шаги"""
    print("\n🎯 РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ:")
    
    if not check_config():
        print("1. Настройте токен бота в config.yaml")
        print("2. Создайте публичный URL (ngrok или туннель)")
        print("3. Настройте Menu Button в @BotFather")
    else:
        print("1. Создайте публичный URL:")
        print("   • Запустите: ngrok http 5000")
        print("   • Или: python tunnel_fix.py")
        print("2. Настройте Menu Button с полученным URL")
        print("3. Протестируйте в Telegram")

def main():
    """Основная функция"""
    print("🚀 Быстрая настройка Telegram Mini App")
    
    # Проверяем статус
    check_app_status()
    
    # Показываем инструкции
    show_setup_instructions()
    
    # Предлагаем следующие шаги
    suggest_next_steps()
    
    print("\n💡 Для помощи обратитесь к файлам:")
    print("   • TELEGRAM_SETUP.md")
    print("   • ЗАПУСК_TELEGRAM_MINI_APP.md")

if __name__ == "__main__":
    main()