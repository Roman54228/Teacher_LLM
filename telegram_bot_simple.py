#!/usr/bin/env python3
"""
Простой Telegram Bot для Interview Prep Mini App
Работает без сложных зависимостей
"""

import requests
import json
import time
import sys
import os

# Добавляем путь к конфигурации
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_loader import config

# Конфигурация
BOT_TOKEN = config.get('telegram.bot_token')
WEB_APP_URL = config.get('telegram.web_app_url', 'http://localhost:5000')

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения через Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    response = requests.post(url, data=data)
    return response.json()

def handle_start_command(chat_id, user_name):
    """Обработка команды /start"""
    welcome_text = f"""🎯 **Добро пожаловать в Interview Prep Bot!**

Привет, {user_name}! Я помогу тебе подготовиться к техническим собеседованиям.

**Что я умею:**
• Тесты по Python, ML, NLP и Computer Vision
• ИИ-объяснения сложных вопросов 
• Отслеживание прогресса и уровня
• Персонализированные рекомендации

**Твой уровень определяется по баллам:**
🥉 Junior (0-59%)
🥈 Middle (60-79%) 
🏆 Senior (80%+)

Нажми кнопку ниже, чтобы начать!"""

    # Создаем кнопки
    keyboard = {
        'inline_keyboard': [
            [{
                'text': '🎯 Начать подготовку',
                'web_app': {'url': WEB_APP_URL}
            }],
            [{'text': 'ℹ️ О боте', 'callback_data': 'about'}],
            [{'text': '📊 Статистика', 'callback_data': 'stats'}]
        ]
    }
    
    send_message(chat_id, welcome_text, keyboard)

def handle_callback(chat_id, message_id, callback_data, user_name):
    """Обработка callback кнопок"""
    if callback_data == 'about':
        about_text = """ℹ️ **О Interview Prep Bot**

Этот бот создан для подготовки к техническим собеседованиям в IT.

**Технологии:**
• YandexGPT для ИИ-объяснений
• SQLite для хранения прогресса
• Telegram Mini Apps для удобного интерфейса

**Категории вопросов:**
🐍 Python - основы языка, структуры данных
🤖 Machine Learning - алгоритмы, метрики
💬 NLP - обработка текста, модели
👁️ Computer Vision - CNN, обработка изображений"""
        
        keyboard = {
            'inline_keyboard': [
                [{'text': '← Назад', 'callback_data': 'back'}]
            ]
        }
        edit_message(chat_id, message_id, about_text, keyboard)
        
    elif callback_data == 'stats':
        stats_text = """📊 **Твоя статистика**

Для просмотра подробной статистики запусти приложение.

**Общие данные:**
• Всего пользователей: 1,000+
• Вопросов в базе: 100+
• Категорий: 4"""
        
        keyboard = {
            'inline_keyboard': [
                [{
                    'text': '📱 Открыть приложение',
                    'web_app': {'url': WEB_APP_URL}
                }],
                [{'text': '← Назад', 'callback_data': 'back'}]
            ]
        }
        edit_message(chat_id, message_id, stats_text, keyboard)
        
    elif callback_data == 'back':
        handle_start_command(chat_id, user_name)

def edit_message(chat_id, message_id, text, reply_markup=None):
    """Редактирование сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    response = requests.post(url, data=data)
    return response.json()

def get_updates(offset=0):
    """Получение обновлений от Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'offset': offset, 'timeout': 30}
    
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

def main():
    """Основной цикл бота"""
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        print("❌ Ошибка: Telegram Bot Token не настроен!")
        print("📝 Для настройки:")
        print("1. Создайте бота у @BotFather в Telegram")
        print("2. Скопируйте токен в config.yaml → telegram.bot_token")
        print("3. Перезапустите бота")
        return
    
    print("🚀 Запуск простого Telegram бота...")
    print(f"🔗 Web App URL: {WEB_APP_URL}")
    print("✓ Bot запущен и готов к работе!")
    print("💬 Попробуйте команду /start в Telegram")
    print("⛔ Для остановки нажмите Ctrl+C")
    
    offset = 0
    
    while True:
        try:
            # Получаем обновления
            updates = get_updates(offset)
            
            if not updates or not updates.get('ok'):
                time.sleep(1)
                continue
                
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                
                # Обработка сообщений
                if 'message' in update:
                    message = update['message']
                    chat_id = message['chat']['id']
                    user_name = message['from'].get('first_name', 'Друг')
                    text = message.get('text', '')
                    
                    if text == '/start':
                        handle_start_command(chat_id, user_name)
                    elif text == '/help':
                        handle_start_command(chat_id, user_name)
                
                # Обработка callback кнопок
                elif 'callback_query' in update:
                    callback = update['callback_query']
                    chat_id = callback['message']['chat']['id']
                    message_id = callback['message']['message_id']
                    callback_data = callback['data']
                    user_name = callback['from'].get('first_name', 'Друг')
                    
                    # Подтверждаем получение callback
                    answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
                    requests.post(answer_url, data={'callback_query_id': callback['id']})
                    
                    handle_callback(chat_id, message_id, callback_data, user_name)
                    
        except KeyboardInterrupt:
            print("\n⛔ Остановка бота...")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()