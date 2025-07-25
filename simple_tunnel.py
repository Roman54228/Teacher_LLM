#!/usr/bin/env python3
"""
Простой скрипт для создания туннеля к Telegram Mini App
"""

import subprocess
import time
import threading
import sys

def start_tunnel():
    """Запускает SSH туннель к localhost.run"""
    try:
        print("🔗 Создаем туннель к localhost.run...")
        
        # Команда для создания туннеля
        cmd = [
            "ssh", 
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-R", "80:localhost:5000",
            "localhost.run"
        ]
        
        # Запускаем туннель
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Ожидаем создания туннеля...")
        
        # Ждем вывода
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"📡 {line.strip()}")
                if "https://" in line:
                    # Извлекаем URL
                    url = line.split("https://")[1].split()[0]
                    full_url = f"https://{url}"
                    print(f"\n✅ Туннель создан: {full_url}")
                    print(f"🔗 Используйте этот URL для настройки Telegram Mini App")
                    
                    # Показываем инструкции
                    show_telegram_instructions(full_url)
                    break
        
        # Держим туннель активным
        print("\n🔄 Туннель активен. Нажмите Ctrl+C для остановки...")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Останавливаем туннель...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Ошибка при создании туннеля: {e}")
        print("💡 Попробуйте запустить: ssh -R 80:localhost:5000 localhost.run")

def show_telegram_instructions(url):
    """Показывает инструкции для настройки Telegram Mini App"""
    print("\n" + "="*60)
    print("📱 ИНСТРУКЦИЯ: Настройка Telegram Mini App")
    print("="*60)
    
    print("\n1️⃣ Создайте бота:")
    print("   • Напишите @BotFather в Telegram")
    print("   • Отправьте /newbot")
    print("   • Введите имя: Interview Prep Bot")
    print("   • Введите username (например: interview_prep_test_bot)")
    print("   • Скопируйте полученный токен")
    
    print("\n2️⃣ Настройте Menu Button:")
    print("   • Напишите @BotFather")
    print("   • Отправьте /mybots")
    print("   • Выберите созданного бота")
    print("   • Bot Settings > Menu Button")
    print("   • Configure menu button")
    print(f"   • URL: {url}")
    print("   • Text: 🎯 Начать тест")
    
    print("\n3️⃣ Добавьте токен в config.yaml:")
    print("   • Откройте файл config.yaml")
    print("   • Замените 'ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ' на ваш токен")
    
    print("\n4️⃣ Протестируйте:")
    print("   • Найдите бота в Telegram")
    print("   • Отправьте /start")
    print("   • Нажмите кнопку меню")
    
    print("\n" + "="*60)
    print("🎯 Готово! Приложение будет работать в Telegram")
    print("="*60)

def main():
    """Основная функция"""
    print("🚀 Запуск туннеля для Telegram Mini App...")
    print("📍 Убедитесь что приложение запущено на порту 5000")
    
    # Запускаем туннель
    start_tunnel()

if __name__ == "__main__":
    main()