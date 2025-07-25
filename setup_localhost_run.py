#!/usr/bin/env python3
"""
Автоматическая настройка localhost.run туннеля для Telegram Mini App
"""

import subprocess
import threading
import time
import re
import sys
import os

# Добавляем путь к конфигурации
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_loader import config

def start_localhost_run():
    """Запуск localhost.run туннеля"""
    print("🚀 Запуск localhost.run туннеля...")
    
    try:
        # Запускаем SSH туннель
        process = subprocess.Popen(
            ['ssh', '-R', '80:localhost:5000', 'localhost.run'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Читаем вывод и ищем URL
        for line in iter(process.stdout.readline, ''):
            print(f"[localhost.run] {line.strip()}")
            
            # Ищем URL в выводе
            url_match = re.search(r'https://[a-zA-Z0-9-]+\.localhost\.run', line)
            if url_match:
                url = url_match.group(0)
                print(f"✅ Туннель создан: {url}")
                print(f"📝 Обновите config.yaml:")
                print(f"   telegram:")
                print(f"     web_app_url: \"{url}\"")
                print(f"🔧 После обновления config.yaml запустите: python telegram_bot_simple.py")
                break
                
    except FileNotFoundError:
        print("❌ SSH не найден!")
        print("💡 Решения:")
        print("  - Windows: Установите Git Bash")
        print("  - Linux: sudo apt install openssh-client")
        print("  - macOS: SSH уже должен быть установлен")
    except KeyboardInterrupt:
        print("\n⛔ Туннель остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_app_running():
    """Проверка что основное приложение запущено"""
    import requests
    try:
        response = requests.get('http://localhost:5000', timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    """Основная функция"""
    print("🎯 Настройка Telegram Mini App с localhost.run")
    print("=" * 50)
    
    # Проверяем что приложение запущено
    if not check_app_running():
        print("❌ Основное приложение не запущено на порту 5000!")
        print("📝 Сначала запустите: python telegram_app.py")
        return
    
    print("✅ Основное приложение работает на localhost:5000")
    
    # Проверяем конфигурацию
    bot_token = config.get('telegram.bot_token')
    if not bot_token or bot_token == "your_telegram_bot_token_here":
        print("❌ Telegram Bot Token не настроен!")
        print("📝 Настройте токен в config.yaml")
        return
    
    print("✅ Telegram Bot Token настроен")
    print("🚀 Создаем туннель через localhost.run...")
    
    # Запускаем туннель
    start_localhost_run()

if __name__ == '__main__':
    main()