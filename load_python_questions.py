#!/usr/bin/env python3
"""
Скрипт для загрузки Python вопросов в базу данных из questions.json
"""
import json
import sys
import os

# Добавляем корневую директорию в path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import DatabaseManager

def load_python_questions():
    """Загружает вопросы Python в базу данных"""
    print("🔄 Загружаем вопросы Python...")
    
    # Инициализируем базу данных
    db_manager = DatabaseManager()
    
    # Загружаем вопросы из JSON файла
    with open('data/questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    # Очищаем старые вопросы категории "Python" если есть
    print("🗑️ Очищаем старые вопросы категории 'Python'...")
    db_manager.clear_category_questions('Python')
    
    # Загружаем новые Python вопросы
    print("➕ Загружаем новые Python вопросы...")
    
    python_questions = questions_data.get('Python', [])
    
    # Загружаем новые Python вопросы напрямую
    count = db_manager.load_questions_to_db({'Python': python_questions})
    
    print(f"✅ Успешно загружено {count} вопросов Python!")
    
    # Проверяем что загрузилось
    python_questions_db = db_manager.get_questions_by_category('Python')
    print(f"📊 В базе данных найдено {len(python_questions_db)} вопросов для категории 'Python'")
    
    # Проверяем подкатегории
    subcategories = db_manager.get_subcategories_by_category('Python')
    print(f"📂 Подкатегории Python: {subcategories}")
    
    return True

if __name__ == "__main__":
    try:
        load_python_questions()
        print("🐍 Python тест готов к использованию!")
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        import traceback
        traceback.print_exc()