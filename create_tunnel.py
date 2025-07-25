#!/usr/bin/env python3
"""
Создание туннеля для Telegram Mini App
"""

import subprocess
import sys
import time
import threading
import re

def create_tunnel():
    """Создает SSH туннель для localhost.run"""
    print("🚀 Создаем туннель для порта 5000...")
    
    # Команда для создания туннеля (как в инструкции)
    cmd = [
        "ssh", 
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-R", "80:localhost:5000",  # Ваше приложение на порту 5000
        "localhost.run"
    ]
    
    try:
        # Запускаем процесс
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print("⏳ Ожидаем создания туннеля...")
        
        # Читаем вывод
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(f"[SSH] {line}")
                
                # Ищем URL в выводе
                if "https://" in line:
                    # Извлекаем URL
                    url_match = re.search(r'https://[^\s]+', line)
                    if url_match:
                        url = url_match.group()
                        print(f"\n✅ Туннель создан: {url}")
                        print(f"🎯 Используйте этот URL для настройки Telegram Mini App")
                        
                        # Обновляем config.yaml
                        update_config(url)
                        
                        # Показываем инструкции
                        show_instructions(url)
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
        return False
    
    return True

def update_config(url):
    """Обновляет config.yaml с новым URL"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Обновляем URL
        content = content.replace(
            'web_app_url: "https://admin.localhost.run"',
            f'web_app_url: "{url}"'
        )
        
        with open('config.yaml', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Обновлен config.yaml с URL: {url}")
        
    except Exception as e:
        print(f"⚠️ Не удалось обновить config.yaml: {e}")

def show_instructions(url):
    """Показывает инструкции для настройки"""
    print("\n" + "="*60)
    print("📱 НАСТРОЙКА TELEGRAM MINI APP")
    print("="*60)
    
    print("\n1️⃣ Создайте бота:")
    print("   • @BotFather → /newbot")
    print("   • Имя: Interview Prep Bot")
    print("   • Username: interview_prep_test_bot")
    print("   • Скопируйте токен")
    
    print("\n2️⃣ Добавьте токен в config.yaml:")
    print("   • Замените 'ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ' на токен")
    
    print("\n3️⃣ Настройте Menu Button:")
    print("   • @BotFather → /mybots → выберите бота")
    print("   • Bot Settings → Menu Button → Configure")
    print(f"   • URL: {url}")
    print("   • Text: 🎯 Начать тест")
    
    print("\n4️⃣ Тестируйте:")
    print("   • Найдите бота в Telegram")
    print("   • /start → нажмите кнопку меню")
    
    print("\n" + "="*60)

def main():
    """Основная функция"""
    print("🔗 Создание туннеля для Telegram Mini App")
    print("📍 Приложение должно работать на localhost:5000")
    
    # Создаем туннель
    create_tunnel()

if __name__ == "__main__":
    main()