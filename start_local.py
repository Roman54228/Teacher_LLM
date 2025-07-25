#!/usr/bin/env python3
"""
Локальный запуск Interview Prep Telegram Mini App
Этот скрипт запускает все компоненты системы
"""

import subprocess
import sys
import time
import os
import signal
import threading
from config_loader import config

def run_app(script_name, port, name):
    """Запуск приложения в отдельном процессе"""
    try:
        print(f"🚀 Запуск {name} на порту {port}...")
        process = subprocess.Popen([sys.executable, script_name], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)
        
        # Читаем вывод процесса
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"[{name}] {line.strip()}")
                
    except KeyboardInterrupt:
        print(f"⛔ Остановка {name}...")
        process.terminate()
    except Exception as e:
        print(f"❌ Ошибка запуска {name}: {e}")

def main():
    """Главная функция запуска"""
    print("🎯 Interview Prep - Telegram Mini App")
    print("=" * 50)
    
    # Проверяем конфигурацию
    try:
        db_url = config.get_database_url()
        print(f"✓ База данных: {db_url.split('://')[0]}://...")
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Создаем потоки для запуска приложений
    processes = []
    
    try:
        # Запуск основного приложения
        main_thread = threading.Thread(
            target=run_app, 
            args=('telegram_app.py', config.get('app.main_port', 5000), 'Main App')
        )
        main_thread.daemon = True
        main_thread.start()
        processes.append(main_thread)
        
        time.sleep(2)  # Даем время запуститься
        
        # Запуск админ-панели
        admin_thread = threading.Thread(
            target=run_app,
            args=('admin.py', config.get('app.admin_port', 5001), 'Admin Panel')
        )
        admin_thread.daemon = True
        admin_thread.start()
        processes.append(admin_thread)
        
        time.sleep(2)
        
        print("\n" + "=" * 50)
        print("🌟 Все сервисы запущены!")
        print(f"📱 Основное приложение: http://localhost:{config.get('app.main_port', 5000)}")
        print(f"⚙️  Админ-панель: http://localhost:{config.get('app.admin_port', 5001)}/admin")
        print("=" * 50)
        print("💡 Для остановки нажмите Ctrl+C")
        
        # Ждем завершения
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⛔ Остановка всех сервисов...")
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
    
    print("👋 Все сервисы остановлены.")

if __name__ == "__main__":
    main()