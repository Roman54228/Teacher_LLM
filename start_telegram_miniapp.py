#!/usr/bin/env python3
"""
Простой скрипт для запуска Telegram Mini App
"""

import os
import sys
import time
import requests
from urllib.parse import urlparse

def check_replit_url():
    """Проверяем доступность Replit URL"""
    try:
        # Получаем ID Replit из переменных окружения
        repl_id = os.environ.get('REPL_ID')
        if not repl_id:
            print("❌ REPL_ID не найден в переменных окружения")
            return None
            
        # Формируем URL
        url = f"https://{repl_id}.replit.app"
        print(f"🔍 Проверяем доступность: {url}")
        
        # Проверяем доступность
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ URL доступен: {url}")
            return url
        else:
            print(f"❌ URL недоступен (код: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при проверке URL: {e}")
        return None

def show_instructions(url):
    """Показываем инструкции для настройки Telegram Mini App"""
    print("\n" + "="*60)
    print("📱 ИНСТРУКЦИЯ: Настройка Telegram Mini App")
    print("="*60)
    
    print("\n1️⃣ Создайте бота:")
    print("   • Напишите @BotFather в Telegram")
    print("   • Отправьте /newbot")
    print("   • Введите имя: Interview Prep Bot")
    print("   • Введите username (например: interview_prep_test_bot)")
    print("   • Скопируйте полученный токен")
    
    print("\n2️⃣ Настройте Mini App:")
    print("   • Снова напишите @BotFather")
    print("   • Отправьте /newapp")
    print("   • Выберите созданного бота")
    print("   • Введите название приложения")
    print("   • Введите описание")
    print(f"   • Web App URL: {url}")
    
    print("\n3️⃣ Добавьте токен в config.yaml:")
    print("   • Откройте файл config.yaml")
    print("   • Замените 'ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ' на ваш токен")
    
    print("\n4️⃣ Протестируйте:")
    print("   • Найдите бота в Telegram")
    print("   • Отправьте /start")
    print("   • Нажмите кнопку 'Открыть приложение'")
    
    print("\n" + "="*60)
    print("🎯 Готово! Приложение будет работать в Telegram")
    print("="*60)

def main():
    """Основная функция"""
    print("🚀 Запуск Telegram Mini App...")
    
    # Проверяем URL
    url = check_replit_url()
    if not url:
        print("❌ Не удалось определить URL приложения")
        return
    
    # Показываем инструкции
    show_instructions(url)
    
    # Проверяем что workflow запущен
    print("\n📊 Проверка статуса приложения...")
    try:
        response = requests.get(f"{url}/api/progress", timeout=5)
        if response.status_code == 200:
            print("✅ Основное приложение работает")
        else:
            print("⚠️ Приложение может быть недоступно")
    except:
        print("⚠️ Не удалось проверить статус приложения")
    
    print("\n🎉 Все готово для запуска Telegram Mini App!")

if __name__ == "__main__":
    main()