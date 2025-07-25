#!/usr/bin/env python3
"""
Production version of Telegram Mini App with fixed scoring logic
Optimized for deployment with proper logging and error handling
"""

import os
import sys
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from utils.database import DatabaseManager
from utils.progress_tracker import ProgressTracker
from utils.yandex_gpt_helper import YandexGPTHelper
from config_loader import config
import uuid
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.get('app.secret_key', 'your-secret-key-here')

# Initialize components
db_manager = DatabaseManager()
progress_tracker = ProgressTracker()

# Initialize YandexGPT helper (safe initialization)
try:
    yandex_helper = YandexGPTHelper()
    print("✓ YandexGPT интеграция активирована")
except Exception as e:
    print(f"⚠️ YandexGPT недоступен: {e}")
    yandex_helper = None

# Routes from telegram_app.py

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
        if telegram_data:
            user_id = f"telegram_{telegram_data.get('id', 'unknown')}"
            session['telegram_user'] = telegram_data
        else:
            # Create guest user
            if 'user_id' not in session:
                browser_fingerprint = request.headers.get('User-Agent', '') + str(request.remote_addr)
                user_id = f"guest_{hashlib.md5(browser_fingerprint.encode()).hexdigest()[:12]}"
                session['user_id'] = user_id
                print(f"Created persistent guest user_id: {user_id}")
            else:
                user_id = session['user_id']
        
        session['user_id'] = user_id
        session.permanent = True
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'telegram_data': telegram_data
        })
    except Exception as e:
        app.logger.error(f"Error in init_user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress')
def get_progress():
    """Get user progress"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
        
        progress_data = progress_tracker.get_overall_progress(user_id)
        print(f"Category progress for user {user_id}: {progress_data.get('categories', [])}")
        print(f"Overall progress data: {progress_data}")
        
        recent_answers = progress_tracker.get_recent_answers(user_id, limit=5)
        print(f"Recent answers: {recent_answers}")
        
        return jsonify({
            'progress': progress_data,
            'recent_answers': recent_answers
        })
    except Exception as e:
        app.logger.error(f"Error getting progress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def get_categories():
    """Get available quiz categories with modules structure"""
    try:
        user_id = session.get('user_id')
        categories_data = db_manager.get_categories_with_modules(user_id)
        return jsonify({'categories': categories_data})
    except Exception as e:
        app.logger.error(f"Error getting categories: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/<category>')
def get_questions(category):
    """Get questions for a category (legacy endpoint)"""
    try:
        questions = db_manager.get_questions_by_category(category)
        return jsonify({'questions': questions})
    except Exception as e:
        app.logger.error(f"Error getting questions for {category}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/subcategory/<category>/<subcategory>/questions')
def get_subcategory_questions(category, subcategory):
    """Get questions for a specific subcategory"""
    try:
        questions = db_manager.get_questions_by_subcategory(category, subcategory)
        return jsonify({'questions': questions})
    except Exception as e:
        app.logger.error(f"Error getting questions for {category}/{subcategory}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit an answer and get immediate feedback"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        category = data.get('category')
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not initialized'}), 400
        
        # Get question from database
        from utils.database import Question
        db = db_manager.get_db()
        try:
            question = db.query(Question).filter(Question.id == question_id).first()
            if not question:
                return jsonify({'error': 'Question not found'}), 404
            
            is_correct = selected_answer == question.correct_answer
            
            # Save answer to database
            progress_tracker.save_answer(
                user_id=user_id,
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                category=category
            )
            
            # Get updated stats
            stats = progress_tracker.get_category_stats(user_id, category)
            
            return jsonify({
                'correct': is_correct,
                'correct_answer': question.correct_answer,
                'explanation': None,
                'stats': {
                    'total': stats['total'],
                    'correct': stats['correct'],
                    'score': stats['score'],
                    'level': stats.get('level', 'Junior')
                }
            })
        finally:
            db.close()
            
    except Exception as e:
        app.logger.error(f"Error submitting answer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/complete', methods=['POST'])
def complete_test():
    """Complete test and get social comparison statistics"""
    try:
        data = request.get_json()
        category = data.get('category')
        subcategory = data.get('subcategory')
        score = data.get('score')
        total_questions = data.get('total_questions')
        
        if not all([category, subcategory, score is not None, total_questions]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get user_id
        user_id = session.get('user_id')
        if not user_id:
            # Create persistent user_id for guest users
            browser_fingerprint = request.headers.get('User-Agent', '') + str(request.remote_addr)
            session_key = session.get('_permanent_session_key')
            if not session_key:
                session_key = hashlib.md5(browser_fingerprint.encode()).hexdigest()[:12]
                session['_permanent_session_key'] = session_key
            user_id = f"guest_{session_key}"
            session['user_id'] = user_id
        
        # Save first test result
        saved = db_manager.save_first_test_result(user_id, category, subcategory, score, total_questions)
        
        # Get social comparison statistics
        social_stats = db_manager.get_test_social_stats(category, subcategory, score)
        
        return jsonify({
            'status': 'success',
            'saved_first_result': saved,
            'social_stats': social_stats
        })
        
    except Exception as e:
        app.logger.error(f"Error completing test: {e}")
        return jsonify({'error': str(e)}), 500

def setup_logging():
    """Setup production logging"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/telegram_mini_app.log', 
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    
    # Set log level based on environment
    log_level = logging.INFO
    if os.environ.get('DEBUG', 'False').lower() == 'true':
        log_level = logging.DEBUG
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler]
    )
    
    # Set Flask app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)

def setup_production_config():
    """Setup production-specific configurations"""
    # Trust proxy headers from Nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Production settings
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Security headers
    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 error: {error}')
        return "Page not found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'500 error: {error}')
        return "Internal server error", 500

def validate_environment():
    """Validate environment variables (warning for missing optional vars)"""
    optional_vars = [
        'YANDEX_API_KEY',
        'YANDEX_FOLDER_ID'
    ]
    
    missing_vars = []
    for var in optional_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        app.logger.warning(f"Optional environment variables not set (AI features disabled): {', '.join(missing_vars)}")
        app.logger.info("App will start without AI features. Add API keys to enable them.")

def main():
    """Main production entry point"""
    print("🚀 Starting Telegram Mini App in production mode...")
    
    try:
        # Setup logging first
        setup_logging()
        app.logger.info("Production logging configured")
        
        # Validate environment (warnings only)
        validate_environment()
        app.logger.info("Environment validation completed")
        
        # Setup production configurations
        setup_production_config()
        app.logger.info("Production configuration applied")
        
        # Get configuration from environment
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        
        app.logger.info(f"Starting server on {host}:{port}")
        print(f"✅ Server starting on {host}:{port}")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()