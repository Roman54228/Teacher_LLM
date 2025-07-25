#!/usr/bin/env python3
"""
Финальный тест всех компонентов системы
"""
import requests
import sqlite3
import json
from utils.database import DatabaseManager

def test_database_direct():
    """Тест прямого доступа к базе данных"""
    print("🔍 Тестирование базы данных напрямую...")
    
    conn = sqlite3.connect('interview_prep.db')
    cursor = conn.cursor()
    
    # Проверяем количество вопросов по категориям
    cursor.execute('SELECT category, sub_category, COUNT(*) FROM questions GROUP BY category, sub_category ORDER BY category, sub_category')
    results = cursor.fetchall()
    
    print("📊 Вопросы в базе данных:")
    for row in results:
        print(f"  {row[0]} -> {row[1] or 'NULL'}: {row[2]} questions")
    
    conn.close()

def test_database_methods():
    """Тест методов DatabaseManager"""
    print("\n🔧 Тестирование методов DatabaseManager...")
    
    db = DatabaseManager()
    
    # Тест скрининговых вопросов
    screening = db.get_questions_by_subcategory('Screening Test', 'Тест')
    print(f"✅ Screening Test -> Тест: {len(screening)} questions")
    
    # Тест Python вопросов
    python_basic = db.get_questions_by_subcategory('Python', 'Основы Python')
    print(f"✅ Python -> Основы Python: {len(python_basic)} questions")
    
    # Тест всех категорий
    categories = db.get_all_categories()
    print(f"✅ Всего категорий: {categories}")

def test_api_endpoints():
    """Тест API эндпоинтов"""
    print("\n🌐 Тестирование API эндпоинтов...")
    
    try:
        # Тест API модулей
        r = requests.get('http://localhost:5000/api/modules', timeout=5)
        modules = r.json()
        print(f"✅ /api/modules: {len(modules)} modules loaded")
        
        # Тест API скрининговых вопросов
        r = requests.get('http://localhost:5000/api/questions/Screening%20Test?subcategory=Тест', timeout=5)
        questions = r.json()
        print(f"✅ Screening Test questions: {len(questions)} questions")
        
        # Тест API Python вопросов
        r = requests.get('http://localhost:5000/api/questions/Python?subcategory=Основы%20Python', timeout=5)
        questions = r.json()
        print(f"✅ Python questions: {len(questions)} questions")
        
    except Exception as e:
        print(f"❌ API Error: {e}")

def main():
    print("🚀 Запуск финального теста системы...\n")
    
    test_database_direct()
    test_database_methods() 
    test_api_endpoints()
    
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    main()