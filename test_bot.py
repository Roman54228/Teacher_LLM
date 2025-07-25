#!/usr/bin/env python3
"""
Простой тест Telegram бота
"""

import sys
import os
sys.path.append('.')

from config_loader import Config

def test_bot_config():
    """Проверяет конфигурацию бота"""
    print("🤖 Проверка конфигурации Telegram бота...")
    
    try:
        config = Config()
        bot_token = config.get('telegram.bot_token')
        web_app_url = config.get('telegram.web_app_url')
        
        print(f"✅ Bot token: {'настроен' if bot_token and bot_token != 'ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ' else '❌ НЕ НАСТРОЕН'}")
        print(f"✅ Web App URL: {web_app_url}")
        
        if bot_token and bot_token != 'ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ':
            print("\n🎯 Готово к тестированию в Telegram!")
            print("1. Убедитесь что ngrok запущен")
            print("2. Настройте Menu Button в @BotFather")
            print("3. Протестируйте в Telegram")
        else:
            print("\n⚠️ Добавьте токен бота в config.yaml")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Основная функция"""
    test_bot_config()

if __name__ == "__main__":
    main()