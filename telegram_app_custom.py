"""
Telegram Mini App - Interview Prep
Beautiful custom frontend with Flask backend (no Streamlit dependencies)
"""
import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from utils.database import db_manager
from utils.db_progress_tracker import DatabaseProgressTracker
from utils.yandex_gpt_helper import get_ai_explanation, get_personalized_recommendations
from config_loader import config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize database
db_manager.create_tables()

@app.route('/')
def index():
    """Main page for Telegram Mini App with beautiful custom design"""
    # Initialize user session
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_user():
    """Initialize user session"""
    data = request.get_json()
    telegram_user_id = data.get('telegram_user_id')
    
    if telegram_user_id:
        session['telegram_user_id'] = telegram_user_id
        session['user_id'] = f"tg_{telegram_user_id}"
    else:
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
    
    # Initialize progress tracker
    progress_tracker = DatabaseProgressTracker(session['user_id'])
    
    return jsonify({
        'status': 'success',
        'user_id': session['user_id']
    })

@app.route('/api/categories')
def get_categories():
    """Get all available categories with progress data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
            
        progress_tracker = DatabaseProgressTracker(user_id)
        categories = db_manager.get_all_categories()
        
        # If no categories in database, load from JSON
        if not categories:
            try:
                # Try Russian questions first, fallback to English
                ru_questions_file = 'data/questions_ru.json'
                en_questions_file = 'data/questions.json'
                
                questions_file = ru_questions_file if os.path.exists(ru_questions_file) else en_questions_file
                
                with open(questions_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    db_manager.load_questions_to_db(json_data)
                    categories = list(json_data.keys())
            except Exception as e:
                print(f"Error loading questions: {e}")
                return jsonify({'error': 'Failed to load questions'}), 500
        
        # Get user progress for each category
        result = []
        for category in categories:
            stats = progress_tracker.get_category_stats(category)
            result.append({
                'name': category,
                'answered': stats.get('answered', 0),
                'total_questions': stats.get('total', 0),
                'score': stats.get('score', 0)
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting categories: {e}")
        return jsonify({'error': 'Failed to get categories'}), 500

@app.route('/api/questions/<category>')
def get_questions(category):
    """Get questions for a specific category"""
    try:
        questions = db_manager.get_questions_by_category(category)
        
        # Format questions for frontend
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                'id': q['id'],
                'question': q['question_text'],
                'options': json.loads(q['options']) if isinstance(q['options'], str) else q['options'],
                'correct_answer': q['correct_answer'],
                'hint': q.get('hint', '')
            })
        
        return jsonify(formatted_questions)
        
    except Exception as e:
        print(f"Error getting questions: {e}")
        return jsonify({'error': 'Failed to get questions'}), 500

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer for a question"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
        
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        category = data.get('category')
        correct_answer = data.get('correct_answer')
        
        if not all([question_id, selected_answer, category, correct_answer]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        is_correct = selected_answer == correct_answer
        
        # Save answer to database
        db_manager.save_user_answer(
            user_id=user_id,
            question_id=question_id,
            category=category,
            selected_answer=selected_answer,
            is_correct=is_correct
        )
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': correct_answer
        })
        
    except Exception as e:
        print(f"Error submitting answer: {e}")
        return jsonify({'error': 'Failed to submit answer'}), 500

@app.route('/api/hint/<int:question_id>')
def get_hint(question_id):
    """Get hint for a question"""
    try:
        # Get question from database
        questions = db_manager.get_questions_by_category("")  # Get all questions
        question = next((q for q in questions if q['id'] == question_id), None)
        
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        hint = question.get('hint', 'Нет подсказки для этого вопроса')
        
        return jsonify({'hint': hint})
        
    except Exception as e:
        print(f"Error getting hint: {e}")
        return jsonify({'error': 'Failed to get hint'}), 500

@app.route('/api/ai-chat/start', methods=['POST'])
def start_ai_chat():
    """Start AI chat session for a question"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        
        # Get question details from database
        # For now, return a simple response
        session['chat_history'] = []
        
        return jsonify({
            'status': 'Chat session started',
            'message': 'Привет! Я готов помочь с объяснением вопроса. Что тебя интересует?'
        })
        
    except Exception as e:
        print(f"Error starting AI chat: {e}")
        return jsonify({'error': 'Failed to start chat'}), 500

@app.route('/api/ai-chat/message', methods=['POST'])
def send_chat_message():
    """Send message to AI chat"""
    try:
        data = request.get_json()
        user_message = data.get('message')
        question_id = data.get('question_id')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get chat history from session
        chat_history = session.get('chat_history', [])
        
        # Add user message to history
        chat_history.append({'role': 'user', 'content': user_message})
        
        # For now, return a simple AI response
        # In production, this would call YandexGPT API
        ai_response = f"Спасибо за вопрос: '{user_message}'. Это отличный вопрос! Давайте разберем его подробнее..."
        
        chat_history.append({'role': 'assistant', 'content': ai_response})
        session['chat_history'] = chat_history
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        print(f"Error sending chat message: {e}")
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/api/progress')
def get_progress():
    """Get user's detailed progress"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
        
        progress_tracker = DatabaseProgressTracker(user_id)
        overall_score = progress_tracker.get_overall_score()
        total_answered = progress_tracker.get_total_questions_answered()
        
        return jsonify({
            'overall_score': overall_score,
            'total_answered': total_answered,
            'categories': []
        })
        
    except Exception as e:
        print(f"Error getting progress: {e}")
        return jsonify({'error': 'Failed to get progress'}), 500

@app.route('/api/recommendations')
def get_recommendations():
    """Get AI-powered recommendations"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
        
        # For now, return simple recommendations
        recommendations = [
            "Изучите основы Python для улучшения результатов",
            "Практикуйте алгоритмы машинного обучения",
            "Углубитесь в изучение NLP технологий"
        ]
        
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@app.route('/api/leaderboard')
def get_leaderboard():
    """Get leaderboard (top users by score)"""
    try:
        # For now, return mock leaderboard
        leaderboard = [
            {'name': 'User1', 'score': 95, 'level': 'Senior'},
            {'name': 'User2', 'score': 87, 'level': 'Middle'},
            {'name': 'User3', 'score': 78, 'level': 'Junior'}
        ]
        
        return jsonify(leaderboard)
        
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        return jsonify({'error': 'Failed to get leaderboard'}), 500

if __name__ == '__main__':
    print("🚀 Запуск Interview Prep Telegram Mini App")
    print("✓ Конфигурация загружена из config.yaml")
    print(f"✓ Используется SQLite база данных: {config.get_database_url()}")
    print("✓ Таблицы базы данных созданы/проверены")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )