#!/usr/bin/env python3
"""
Скрипт для перезагрузки вопросов из JSON в базу данных
"""
import json
from utils.database import DatabaseManager
from config_loader import config

def reload_questions():
    """Перезагрузить вопросы из JSON файла в базу данных"""
    db_manager = DatabaseManager()
    
    # Загрузить вопросы из JSON
    with open('data/questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    print("Загружаю обновленные вопросы в базу данных...")
    
    # Очистить и перезагрузить вопросы
    db = db_manager.get_db()
    try:
        # Удалить все существующие вопросы
        from utils.database import Question
        db.query(Question).delete()
        db.commit()
        print("Старые вопросы удалены")
        
        # Загрузить новые вопросы
        for category, questions in questions_data.items():
            for q_data in questions:
                question = Question(
                    category=category,
                    sub_category=q_data.get('sub_category'),
                    question_text=q_data['question'],
                    options=json.dumps(q_data['options']),
                    correct_answer=q_data['correct_answer'],
                    hint=q_data.get('hint')
                )
                db.add(question)
        
        db.commit()
        print(f"Загружено {sum(len(questions) for questions in questions_data.values())} вопросов")
        
        # Показать статистику по категориям
        for category, questions in questions_data.items():
            print(f"  {category}: {len(questions)} вопросов")
            
    finally:
        db.close()

if __name__ == "__main__":
    reload_questions()
    print("Готово!")