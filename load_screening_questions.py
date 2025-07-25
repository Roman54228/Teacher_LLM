#!/usr/bin/env python3
"""
Скрипт для загрузки вопросов скринингового теста в базу данных
"""
import json
import sys
import os

# Добавляем корневую директорию в path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import DatabaseManager

def load_screening_questions():
    """Загружает вопросы скринингового теста в базу данных"""
    print("🔄 Загружаем вопросы скринингового теста...")
    
    # Инициализируем базу данных
    db_manager = DatabaseManager()
    
    # Загружаем вопросы из JSON файла
    with open('data/screening_test_questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    # Очищаем старые вопросы категории "Screening Test" если есть
    print("🗑️ Очищаем старые вопросы категории 'Screening Test'...")
    db_manager.clear_category_questions('Screening Test')
    
    # Загружаем новые вопросы
    print("➕ Загружаем новые вопросы...")
    count = db_manager.load_questions_to_db(questions_data)
    
    print(f"✅ Успешно загружено {count} вопросов для скринингового теста!")
    
    # Проверяем что загрузилось
    screening_questions = db_manager.get_questions_by_category('Screening Test')
    print(f"📊 В базе данных найдено {len(screening_questions)} вопросов для категории 'Screening Test'")
    
    # Проверяем подкатегории
    subcategories = db_manager.get_subcategories_by_category('Screening Test')
    print(f"📂 Подкатегории: {subcategories}")
    
    return True

if __name__ == "__main__":
    try:
        load_screening_questions()
        print("🎯 Скрининговый тест готов к использованию!")
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        import traceback
        traceback.print_exc()