#!/usr/bin/env python3
"""
Production version of Telegram Mini App with fixed imports and working logic
Optimized for deployment with proper logging and error handling
"""

import os
import sys
import hashlib
import logging
import json
from logging.handlers import RotatingFileHandler
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from utils.database import DatabaseManager
from utils.progress_tracker import ProgressTracker
from config_loader import config
import uuid
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.get('app.secret_key', 'your-secret-key-here')

# Initialize components
db_manager = DatabaseManager()

# Initialize YandexGPT helper (safe initialization)
yandex_helper = None
try:
    from utils.yandex_gpt_helper import YandexGPTHelper
    yandex_helper = YandexGPTHelper()
    print("✓ YandexGPT интеграция активирована")
except Exception as e:
    print(f"⚠️ YandexGPT недоступен: {e}")

# Static file serving for images
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files including uploaded images"""
    return send_from_directory('static', filename)

# Routes
@app.route('/')
def index():
    """Main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error rendering index: {e}")
        return f"Application error: {e}", 500

@app.route('/api/init', methods=['POST'])
def init_user():
    """Initialize user with Telegram data"""
    try:
        data = request.get_json() or {}
        telegram_data = data.get('telegram_data', {})
        
        # Create user session
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
        
        # Store Telegram data in session
        if telegram_data:
            session['telegram_data'] = telegram_data
            
        return jsonify({
            'status': 'success',
            'user_id': session['user_id']
        })
        
    except Exception as e:
        app.logger.error(f"Error initializing user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress')
def get_progress():
    """Get user progress data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
            
        # Get user progress from database
        progress = db_manager.get_user_progress(user_id)
        
        # Format for frontend
        formatted_progress = {
            'total_answered': progress.get('total_answered', 0),
            'overall_score': progress.get('overall_score', 0),
            'categories': []
        }
        
        # Convert categories to expected format
        categories_data = progress.get('categories', [])
        if isinstance(categories_data, list):
            formatted_progress['categories'] = categories_data
        else:
            # Convert dict to list if needed
            for category_name, category_data in categories_data.items():
                formatted_progress['categories'].append({
                    'name': category_name,
                    'answered': category_data.get('total', 0),
                    'score': category_data.get('score', 0)
                })
        
        return jsonify(formatted_progress)
        
    except Exception as e:
        app.logger.error(f"Error getting progress: {e}")
        return jsonify({
            'total_answered': 0,
            'overall_score': 0,
            'categories': []
        }), 500

@app.route('/api/profile')
def get_profile():
    """Get user profile data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
            
        telegram_data = session.get('telegram_data', {})
        
        # Get user progress from database
        total_questions = 0
        total_correct = 0
        categories_progress = {}
        
        try:
            # Get basic stats from database
            user_answers = db_manager.get_user_answers(user_id) if hasattr(db_manager, 'get_user_answers') else []
            total_questions = len(user_answers)
            total_correct = sum(1 for answer in user_answers if answer.get('is_correct', False))
        except:
            pass
        
        return jsonify({
            'telegram_data': telegram_data,
            'progress': {
                'total_questions': total_questions,
                'total_correct': total_correct,
                'categories': categories_progress
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error getting profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/modules')
def get_modules():
    """Get available modules from database"""
    try:
        # Load modules from database
        modules = []
        try:
            db_modules = db_manager.get_all_modules()
            
            for module in db_modules:
                # Get subcategories/topics for this module from questions table
                topics = []
                try:
                    # Map module names to categories in questions table
                    category_mapping = {
                        'Screening Test': 'Screening Test',
                        'screening_test': 'Screening Test',
                        'Python': 'Python',
                        'python': 'Python',
                        'Machine Learning': 'Machine Learning',
                        'machine_learning': 'Machine Learning',
                        'NLP': 'NLP',
                        'nlp': 'NLP',
                        'Computer Vision': 'Computer Vision',
                        'computer_vision': 'Computer Vision'
                    }
                    
                    # Get the correct category name for questions
                    category_name = category_mapping.get(module['name'], module['name'])
                    
                    # Get unique subcategories for this module
                    unique_subcategories = db_manager.get_subcategories_for_module(category_name)
                    
                    for subcategory in unique_subcategories:
                        # Count questions for this subcategory
                        question_count = db_manager.count_questions_by_subcategory(category_name, subcategory['name'])
                        
                        topics.append({
                            'id': subcategory['name'].lower().replace(' ', '_'),
                            'name': subcategory['name'],
                            'description': subcategory.get('description', f"Вопросы по {subcategory['name']}"),
                            'icon': subcategory.get('icon', '📝'),
                            'questions_count': question_count
                        })
                        
                    # If no subcategories found, check for questions without subcategory
                    if not topics:
                        question_count = db_manager.count_questions_by_category(category_name)
                        if question_count > 0:
                            topics = [{
                                'id': 'general',
                                'name': 'Общие вопросы',
                                'description': f"Вопросы по {module['name']}",
                                'icon': '📝',
                                'questions_count': question_count
                            }]
                        
                except Exception as e:
                    app.logger.warning(f"Could not load topics for module {module['name']}: {e}")
                    # Add default topic if no subcategories found
                    topics = [{
                        'id': 'general',
                        'name': 'Общие вопросы',
                        'description': f"Вопросы по {module['name']}",
                        'icon': '📝',
                        'questions_count': 0
                    }]
                
                modules.append({
                    'id': module['name'].lower().replace(' ', '_'),
                    'name': module['name'],
                    'emoji': module.get('icon', '📚'),
                    'description': module.get('description', f"Модуль {module['name']}"),
                    'is_premium': module.get('is_premium', False),
                    'accessible': not module.get('is_premium', False),  # For premium module access checking
                    'topics': topics
                })
                
        except Exception as e:
            app.logger.warning(f"Could not load modules from database: {e}")
            # Fallback to hardcoded modules if database fails
            modules = [
                {
                    "id": "screening_test",
                    "name": "Скрининговый тест",
                    "emoji": "🎯",
                    "description": "Общий тест для оценки базовых навыков",
                    "is_premium": False,
                    "accessible": True,
                    "topics": [
                        {
                            "id": "quick_assessment", 
                            "name": "Общая оценка",
                            "description": "15 вопросов по математике, Python и ML",
                            "icon": "⚡",
                            "questions_count": 15
                        }
                    ]
                }
            ]
            
        return jsonify(modules)
        
    except Exception as e:
        app.logger.error(f"Error loading modules: {e}")
        return jsonify([]), 500

@app.route('/api/questions/<category>')
def get_questions(category):
    """Get questions for category"""
    try:
        subcategory = request.args.get('subcategory')
        
        # Get questions from database
        if subcategory:
            questions = db_manager.get_questions_by_subcategory(category, subcategory)
        else:
            questions = db_manager.get_questions_by_category(category)
        
        return jsonify(questions)
        
    except Exception as e:
        app.logger.error(f"Error getting questions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/subcategory/<category>/<subcategory>/questions')
def get_subcategory_questions(category, subcategory):
    """Get questions for specific subcategory - new API format"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
        
        # Check if module is premium and user has access
        is_premium, price, display_name = db_manager.is_module_premium(category)
        
        if is_premium:
            # Check if user has purchased this module
            user_purchases = session.get('purchased_modules', [])
            if category not in user_purchases:
                return jsonify({
                    'error': 'premium_required',
                    'module_name': display_name,
                    'price': price,
                    'message': f'Модуль "{display_name}" требует покупки за {price} ₽'
                }), 402  # Payment required
        
        # Map frontend category names to database category names
        category_mapping = {
            'screening_test': 'Screening Test',
            'python': 'Python',
            'machine_learning': 'Machine Learning',
            'nlp': 'NLP',
            'computer_vision': 'Computer Vision'
        }
        
        # Map frontend subcategory names to database subcategory names  
        subcategory_mapping = {
            'Общая оценка': 'Тест',
            'Тест': 'Тест',
            'Основы Python': 'Основы Python'
        }
        
        # Map category and subcategory names
        db_category = category_mapping.get(category, category)
        db_subcategory = subcategory_mapping.get(subcategory, subcategory)
        
        app.logger.info(f"Mapped {category}/{subcategory} -> {db_category}/{db_subcategory}")
        
        # Get questions from database
        questions = db_manager.get_questions_by_subcategory(db_category, db_subcategory)
        
        return jsonify({'questions': questions})
        
    except Exception as e:
        app.logger.error(f"Error getting subcategory questions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit an answer"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
            
        question_id = data.get('question_id')
        selected_answer = data.get('answer')
        
        # Validate that selected_answer is not None or empty
        if selected_answer is None or selected_answer == '':
            app.logger.error(f"Empty answer received: {data}")
            return jsonify({'error': 'Answer is required'}), 400
            
        app.logger.info(f"Received answer: question_id={question_id}, answer={selected_answer}")
        
        # Get question from database
        question = db_manager.get_question_by_id(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
            
        # Check if answer is correct
        correct_answers = question.get('correct_answers', [])
        is_correct = selected_answer in correct_answers
        
        # Save answer to database
        try:
            db_manager.save_user_answer(
                user_id=user_id,
                question_id=question_id,
                category=question.get('category', ''),
                selected_answer=selected_answer,
                is_correct=is_correct
            )
        except Exception as e:
            app.logger.warning(f"Could not save answer to database: {e}")
        
        return jsonify({
            'correct': is_correct,
            'explanation': question.get('hint', '')
        })
        
    except Exception as e:
        app.logger.error(f"Error submitting answer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/complete', methods=['POST'])
def complete_test():
    """Complete test and get social statistics"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
            
        category = data.get('category')
        subcategory = data.get('subcategory')
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 10)
        
        # Calculate score percentage
        score_percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        # Save first test result for social comparison
        try:
            # Check if this is first attempt
            existing_result = db_manager.get_first_test_result(user_id, category, subcategory)
            if not existing_result:
                db_manager.save_first_test_result(
                    user_id=user_id,
                    category=category,
                    subcategory=subcategory,
                    score=score,
                    total_questions=total_questions,
                    score_percentage=score_percentage
                )
        except Exception as e:
            app.logger.warning(f"Could not save test result: {e}")
        
        # Get social statistics
        social_stats = {}
        try:
            social_stats = db_manager.get_social_statistics(category, subcategory)
        except Exception as e:
            app.logger.warning(f"Could not get social stats: {e}")
            social_stats = {
                'average_score': 0,
                'total_attempts': 0,
                'percentile': 50
            }
        
        return jsonify({
            'score': score,
            'total_questions': total_questions,
            'score_percentage': score_percentage,
            'social_stats': social_stats
        })
        
    except Exception as e:
        app.logger.error(f"Error completing test: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Chat with AI assistant"""
    try:
        if not yandex_helper:
            return jsonify({'error': 'AI помощник недоступен'}), 503
            
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', {})
        
        response = yandex_helper.get_explanation(message, context)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        app.logger.error(f"Error in AI chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def get_categories():
    """Get all categories (legacy endpoint)"""
    try:
        # Get categories from database
        categories = []
        try:
            if hasattr(db_manager, 'get_all_categories'):
                categories = db_manager.get_all_categories()
            else:
                # Fallback categories
                categories = [
                    {"name": "Screening Test", "description": "Общий тест"},
                    {"name": "Python", "description": "Python программирование"},
                    {"name": "Machine Learning", "description": "Машинное обучение"},
                    {"name": "NLP", "description": "Обработка естественного языка"}
                ]
        except Exception as e:
            app.logger.warning(f"Could not get categories from database: {e}")
            categories = []
            
        return jsonify(categories)
        
    except Exception as e:
        app.logger.error(f"Error getting categories: {e}")
        return jsonify([]), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/purchase_module', methods=['POST'])
def purchase_module():
    """Handle module purchase through Telegram payments"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
            
        module_name = data.get('module_name')
        telegram_user_id = session.get('telegram_id')
        
        # Get module information
        is_premium, price, display_name = db_manager.is_module_premium(module_name)
        
        if not is_premium:
            return jsonify({'error': 'Module is not premium'}), 400
        
        # Create Telegram payment invoice
        if telegram_user_id:
            payment_url = create_telegram_payment(telegram_user_id, module_name, display_name, price)
            return jsonify({
                'payment_url': payment_url,
                'price': price,
                'module_name': display_name
            })
        else:
            # For testing without Telegram - simulate purchase
            user_purchases = session.get('purchased_modules', [])
            if module_name not in user_purchases:
                user_purchases.append(module_name)
                session['purchased_modules'] = user_purchases
            
            return jsonify({
                'success': True,
                'message': f'Модуль "{display_name}" успешно приобретен!',
                'test_mode': True
            })
        
    except Exception as e:
        app.logger.error(f"Error purchasing module: {e}")
        return jsonify({'error': str(e)}), 500

def create_telegram_payment(user_id, module_name, display_name, price):
    """Create Telegram payment invoice"""
    try:
        # This would integrate with Telegram Bot API for real payments
        # For now, return a test payment URL
        return f"https://t.me/your_bot?start=pay_{module_name}_{user_id}_{int(price*100)}"
    except Exception as e:
        app.logger.error(f"Error creating payment: {e}")
        return None

@app.route('/api/check_module_access/<module_name>')
def check_module_access(module_name):
    """Check if user has access to a module"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
        
        # Check if module is premium
        is_premium, price, display_name = db_manager.is_module_premium(module_name)
        
        if not is_premium:
            return jsonify({
                'has_access': True,
                'is_premium': False,
                'module_name': display_name
            })
        
        # Check if user has purchased this module
        user_purchases = session.get('purchased_modules', [])
        has_access = module_name in user_purchases
        
        return jsonify({
            'has_access': has_access,
            'is_premium': True,
            'price': price,
            'module_name': display_name
        })
        
    except Exception as e:
        app.logger.error(f"Error checking module access: {e}")
        return jsonify({'error': str(e)}), 500

def setup_logging():
    """Setup production logging"""
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/telegram_app.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Telegram Mini App startup')

if __name__ == '__main__':
    print("🚀 Starting Telegram Mini App in production mode...")
    
    # Setup logging
    setup_logging()
    
    # Configure app for production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Get configuration
    host = config.get('server.host', '0.0.0.0')
    port = int(config.get('server.port', 5000))
    debug = config.get('server.debug', False)
    
    print(f"✅ Server starting on {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )