import os
import json
import uuid
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session
from utils.database import db_manager
from utils.db_progress_tracker import DatabaseProgressTracker
from utils.yandex_gpt_helper import get_ai_explanation, get_personalized_recommendations
from config_loader import config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.permanent_session_lifetime = timedelta(days=7)  # Sessions last 7 days

# Initialize database
db_manager.create_tables()

def validate_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Validate Telegram WebApp initData
    Based on: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    try:
        # Parse query string
        parsed_data = urllib.parse.parse_qsl(init_data)
        
        # Extract hash and other data
        data_dict = dict(parsed_data)
        received_hash = data_dict.pop('hash', None)
        
        if not received_hash:
            return False
        
        # Create data check string
        data_check_string = '\n'.join(sorted(f'{k}={v}' for k, v in data_dict.items()))
        
        # Create secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        return hmac.compare_digest(calculated_hash, received_hash)
    
    except Exception as e:
        print(f"Error validating Telegram data: {e}")
        return False

def validate_telegram_data_structured(data_check_string: str, received_hash: str, bot_token: str) -> bool:
    """
    Validate Telegram WebApp data using pre-structured data
    Based on the JavaScript implementation provided
    """
    try:
        if not received_hash or not data_check_string:
            return False
        
        # Create secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        return hmac.compare_digest(calculated_hash, received_hash)
    
    except Exception as e:
        print(f"Error validating structured Telegram data: {e}")
        return False

@app.route('/')
def index():
    """Main page for Telegram Mini App"""
    # Initialize user session
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_user():
    """Initialize user session with Telegram auth"""
    try:
        data = request.get_json() or {}
        
        # Extract user data based on auth type
        auth_type = data.get('auth_type', 'guest')  # 'telegram', 'google', 'guest'
        user_data = data.get('user_data', {})
        
        # Generate session ID and make session permanent
        session_id = str(uuid.uuid4())
        session.permanent = True
        
        # Handle different auth types
        if auth_type == 'telegram':
            telegram_data = data.get('telegram_user', user_data)
            validation_data = data.get('validation_data')
            init_data = data.get('init_data', '')
            
            # Validate Telegram data using improved method
            bot_token = config.get('telegram.bot_token')
            is_valid_telegram = False
            
            if validation_data and bot_token:
                # Use structured validation data
                is_valid_telegram = validate_telegram_data_structured(
                    validation_data.get('dataCheckString', ''),
                    validation_data.get('hash', ''),
                    bot_token
                )
                print(f"Telegram structured validation: {'VALID' if is_valid_telegram else 'INVALID'}")
            elif init_data and bot_token:
                # Fallback to old method
                is_valid_telegram = validate_telegram_init_data(init_data, bot_token)
                print(f"Telegram legacy validation: {'VALID' if is_valid_telegram else 'INVALID'}")
            
            if not is_valid_telegram and (init_data or validation_data):
                print("Warning: Telegram data validation failed, using demo user")
                # Create demo user for invalid/test data
                telegram_data = {
                    'id': int(datetime.now().timestamp() * 1000),
                    'first_name': 'Demo',
                    'last_name': 'Пользователь',
                    'username': f'demo_user_{int(datetime.now().timestamp())}',
                    'language_code': 'ru'
                }
            
            telegram_id = str(telegram_data.get('id')) if telegram_data and telegram_data.get('id') else None
            print(f"Telegram user data: {telegram_data}")
            print(f"Telegram ID: {telegram_id}")
            print(f"Data validity: {'VALIDATED' if is_valid_telegram else 'DEMO/TEST'}")
            
            user_id = db_manager.get_or_create_user(
                session_id=session_id,
                telegram_id=telegram_id,
                telegram_data=telegram_data
            )
        elif auth_type == 'google':
            google_data = user_data
            google_id = google_data.get('sub') or google_data.get('id')
            
            # For Google auth, use email as unique identifier
            user_id = db_manager.get_or_create_user(
                session_id=session_id,
                telegram_id=None,  # No telegram for Google users
                telegram_data={
                    'first_name': google_data.get('given_name', google_data.get('name', '')).split()[0] if google_data.get('given_name') or google_data.get('name') else 'Google User',
                    'last_name': google_data.get('family_name', ''),
                    'username': google_data.get('email', '').split('@')[0],
                    'google_id': google_id,
                    'email': google_data.get('email')
                }
            )
        else:
            # Guest user
            user_id = db_manager.get_or_create_user(session_id=session_id)
        
        # Store in session
        session['user_id'] = user_id
        session['session_id'] = session_id
        session['auth_type'] = auth_type
        
        # Get user profile
        profile = db_manager.get_user_profile(user_id)
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'user_id': user_id,
            'auth_type': auth_type,
            'profile': profile
        })
    except Exception as e:
        print(f"Error in init_user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/modules')
def get_modules():
    """Get all available modules (categories) with their subcategories"""
    try:
        categories = db_manager.get_all_categories()
        
        # If no categories, load from JSON
        if not categories:
            try:
                ru_questions_file = 'data/questions_ru.json'
                en_questions_file = 'data/questions.json'
                
                questions_file = ru_questions_file if os.path.exists(ru_questions_file) else en_questions_file
                
                with open(questions_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    db_manager.load_questions_to_db(json_data)
                    categories = list(json_data.keys())
                    print(f"Вопросы загружены из файла: {questions_file}")
            except FileNotFoundError:
                return jsonify({'error': 'Questions not found'}), 404
        
        # Get user ID from session for progress tracking
        # Get user ID from session with persistence for guest users
        user_id = session.get('user_id')
        if not user_id:
            # Create persistent user_id for guest users
            import hashlib
            browser_fingerprint = request.headers.get('User-Agent', '') + str(request.remote_addr)
            session_key = session.get('_permanent_session_key')
            if not session_key:
                session_key = hashlib.md5(browser_fingerprint.encode()).hexdigest()[:12]
                session['_permanent_session_key'] = session_key
            
            user_id = f"guest_{session_key}"
            session['user_id'] = user_id
            session.permanent = True
            print(f"Created persistent guest user_id for modules: {user_id}")
        progress_tracker = DatabaseProgressTracker(user_id)
        
        # Category metadata with icons, colors and premium status
        category_metadata = {
            'Screening Test': {'icon': '🎯', 'color': '#FF6B35', 'description': 'Быстрая оценка вашего уровня по всем направлениям', 'premium': False},
            'Python': {'icon': '🐍', 'color': '#3776AB', 'description': 'Основы языка Python и его применение', 'premium': False},
            'Machine Learning': {'icon': '🤖', 'color': '#FF6B35', 'description': 'Основы машинного обучения и алгоритмы', 'premium': True}, 
            'NLP': {'icon': '💬', 'color': '#30D158', 'description': 'Обработка естественного языка', 'premium': True},
            'Computer Vision': {'icon': '👁️', 'color': '#FF9500', 'description': 'Компьютерное зрение и обработка изображений', 'premium': True},
            'Deep Learning': {'icon': '🧠', 'color': '#007AFF', 'description': 'Глубокое обучение и нейронные сети', 'premium': True},
            'Data Science': {'icon': '📊', 'color': '#34C759', 'description': 'Анализ данных и статистика', 'premium': True},
            'Algorithms': {'icon': '⚡', 'color': '#FF3B30', 'description': 'Алгоритмы и структуры данных', 'premium': True},
            'DevOps': {'icon': '🔧', 'color': '#8E8E93', 'description': 'Развертывание и автоматизация', 'premium': True},
            'Web Development': {'icon': '🌐', 'color': '#5856D6', 'description': 'Веб-разработка и фреймворки', 'premium': True},
            'Database': {'icon': '🗄️', 'color': '#AF52DE', 'description': 'Базы данных и SQL', 'premium': True}
        }
        
        modules_data = []  # Initialize empty list
        
        # Sort categories: free modules first (Screening Test, Python), then premium
        def category_sort_key(category):
            metadata = category_metadata.get(category, {'premium': True})
            is_premium = metadata.get('premium', True)
            
            # Screening Test always first
            if category == 'Screening Test':
                return (0, category)
            # Free modules next
            elif not is_premium:
                return (1, category)
            # Premium modules last
            else:
                return (2, category)
        
        all_categories = sorted(categories, key=category_sort_key)
        
        for category in all_categories:
                
            # Get subcategories for this category
            subcategories = db_manager.get_subcategories_by_category(category)
            print(f"Category {category} subcategories from DB: {subcategories}")
            
            # Get metadata for category
            metadata = category_metadata.get(category, {
                'icon': '📚', 
                'color': '#666666', 
                'description': f'Вопросы по теме {category}'
            })
            
            # Build subcategories data
            submodules = []
            total_questions_in_category = 0
            
            if subcategories:
                # Category has subcategories
                for subcategory in subcategories:
                    questions = db_manager.get_questions_by_subcategory(category, subcategory)
                    question_count = len(questions)
                    total_questions_in_category += question_count
                    
                    # Get progress for this specific subcategory - use the same user_id as above
                    try:
                        print(f"Getting subcategory stats for user {user_id}")
                        
                        subcategory_stats = db_manager.get_subcategory_stats(user_id, category, subcategory)
                        print(f"Subcategory stats for {category} - {subcategory}: {subcategory_stats}")
                    except Exception as e:
                        print(f"Error getting subcategory stats: {e}")
                        subcategory_stats = {'total': 0, 'correct': 0, 'score': 0.0, 'level': 'Junior'}
                    
                    # Debug: show question IDs for this subcategory
                    try:
                        question_ids = [q['id'] for q in questions]
                        print(f"Questions in {category} - {subcategory}: IDs {question_ids}")
                    except Exception as e:
                        print(f"Error getting question IDs: {e}")
                        question_ids = []
                    
                    # Debug subcategory data being sent to frontend
                    print(f"Subcategory {subcategory} final data: score={subcategory_stats['score']}, total={subcategory_stats['total']}")
                    
                    submodules.append({
                        'id': f'{category}_{subcategory}',
                        'name': subcategory,
                        'description': f'Задачи по {subcategory.lower()}',
                        'icon': '🎯',
                        'difficulty': 'Mixed',
                        'total_questions': question_count,
                        'answered': subcategory_stats['total'],
                        'score': subcategory_stats['score'],
                        'level': subcategory_stats.get('level', 'Junior')
                    })
            else:
                # Category has no subcategories, show all questions as one submodule
                questions = db_manager.get_questions_by_category(category)
                question_count = len(questions)
                total_questions_in_category = question_count
                
                stats = progress_tracker.get_category_stats(category)
                
                submodules.append({
                    'id': f'{category}_general',
                    'name': 'Общие вопросы',
                    'description': f'Все вопросы по {category}',
                    'icon': '🎯',
                    'difficulty': 'Mixed',
                    'total_questions': question_count,
                    'answered': stats['total'],
                    'score': stats['score'],
                    'level': stats.get('level', 'Junior')
                })
            
            # Check if user has premium access
            has_premium = check_user_premium(user_id)
            is_premium_module = metadata.get('premium', False)
            
            # Calculate overall completion percentage for this category
            category_stats = progress_tracker.get_category_stats(category)
            completion_pct = int((category_stats['total'] / total_questions_in_category) * 100) if total_questions_in_category > 0 else 0
            
            modules_data.append({
                'id': category,
                'name': category,
                'description': metadata['description'],
                'icon': metadata['icon'],
                'color': metadata['color'],
                'total_questions': total_questions_in_category,
                'completion_percentage': completion_pct,
                'submodules': submodules,
                'premium': is_premium_module,
                'accessible': not is_premium_module or has_premium
            })
        
        return jsonify({
            'modules': modules_data,
            'overall_progress': {
                'total_answered': progress_tracker.get_total_questions_answered(),
                'overall_score': progress_tracker.get_overall_score()
            },
            'user_premium': check_user_premium(user_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Keep old endpoint for backward compatibility
@app.route('/api/categories')
def get_categories():
    """Get all available categories (legacy endpoint)"""
    return get_modules()

@app.route('/api/questions/<category>')
def get_questions(category):
    """Get questions for a specific category (legacy endpoint)"""
    try:
        # Handle special screening test
        if category == 'screening':
            # Get questions directly from Screening Test category
            questions = db_manager.get_questions_by_category('Screening Test')
            questions_data = []
            
            for question in questions:
                questions_data.append({
                    'id': question['id'],
                    'question': question['question'],
                    'options': question['options'],
                    'has_hint': bool(question.get('hint'))
                })
            
            return jsonify({'questions': questions_data})
        
        # Handle regular categories
        questions = db_manager.get_questions_by_category(category)
        questions_data = []
        
        for question in questions:
            questions_data.append({
                'id': question['id'],
                'question': question['question'],
                'options': question['options'],
                'has_hint': bool(question.get('hint'))
            })
        
        return jsonify({'questions': questions_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submodule/<string:submodule_id>/questions')
def get_submodule_questions(submodule_id):
    """Get questions for a specific submodule"""
    try:
        # Handle special screening test
        if submodule_id == 'screening_quick_assessment':
            return get_questions('screening')
        
        # Handle numeric submodule IDs
        if submodule_id.isdigit():
            questions = db_manager.get_questions_by_submodule(int(submodule_id))
        else:
            # Handle string-based submodule IDs like 'Python_general'
            return jsonify({'error': 'Submodule not found'}), 404
        
        if not questions:
            return jsonify({'error': 'No questions found for this submodule'}), 404
        
        questions_data = []
        for question in questions:
            questions_data.append({
                'id': question['id'],
                'question': question['question'],
                'options': question['options'],
                'has_hint': bool(question.get('hint'))
            })
        
        return jsonify({'questions': questions_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subcategory/<category>/<subcategory>/questions')
def get_subcategory_questions(category, subcategory):
    """Get questions for a specific subcategory"""
    try:
        # Use unified approach for all categories including Screening Test
        questions = db_manager.get_questions_by_subcategory(category, subcategory)
        
        if not questions:
            return jsonify({'error': 'No questions found for this subcategory'}), 404
        
        questions_data = []
        for question in questions:
            questions_data.append({
                'id': question['id'],
                'question': question['question'],
                'options': question['options'],
                'has_hint': bool(question.get('hint'))
            })
        
        return jsonify({
            'category': category,
            'subcategory': subcategory,
            'questions': questions_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit an answer for a question"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        category = data.get('category')
        
        if not all([question_id, selected_answer, category]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Handle math questions for screening test
        if str(question_id).startswith('math_'):
            # Define correct answers for math questions
            math_answers = {
                'math_1': '120',
                'math_2': '2x', 
                'math_3': '3',
                'math_4': '25%',
                'math_5': '17'
            }
            
            correct_answer = math_answers.get(question_id)
            is_correct = selected_answer == correct_answer
            
            # Save answer to database for screening test with correct category
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Пользователь не авторизован'}), 401
            
            # Save answer using database manager (category = Screening Test for math questions)
            db_manager.save_user_answer(
                user_id=user_id,
                question_id=question_id,
                category='Screening Test',
                selected_answer=selected_answer,
                is_correct=is_correct
            )
            
            # Get updated stats for screening category
            stats = db_manager.get_category_stats(user_id, 'Screening Test')
            
            return jsonify({
                'correct': is_correct,
                'correct_answer': correct_answer,
                'explanation': 'Математический вопрос в рамках скринингового теста',
                'stats': {
                    'total': stats['total'],
                    'correct': stats['correct'],
                    'score': stats['score'],
                    'level': stats.get('level', 'Junior')
                }
            })
        
        # Get user ID from session with persistence
        user_id = session.get('user_id')
        if not user_id:
            # Create persistent user_id for guest users
            import hashlib
            browser_fingerprint = request.headers.get('User-Agent', '') + str(request.remote_addr)
            session_key = session.get('_permanent_session_key')
            if not session_key:
                session_key = hashlib.md5(browser_fingerprint.encode()).hexdigest()[:12]
                session['_permanent_session_key'] = session_key
            
            user_id = f"guest_{session_key}"
            session['user_id'] = user_id
            session['session_id'] = user_id
            session.permanent = True
            print(f"Created persistent guest user_id for submit_answer: {user_id}")
        
        print(f"Submitting answer - user_id: {user_id}, question_id: {question_id}, answer: {selected_answer}")
        
        # Get the correct answer from database for regular questions
        from utils.database import Question
        db = db_manager.get_db()
        try:
            question = db.query(Question).filter(
                Question.id == question_id
            ).first()
            
            if not question:
                print(f"Question with id {question_id} not found in database")
                return jsonify({'error': 'Question not found'}), 404
            
            correct_answer = question.correct_answer
            is_correct = selected_answer == correct_answer
            
            print(f"Question found - correct_answer: {correct_answer}, is_correct: {is_correct}")
            
            # Use 'Screening Test' category if this is part of screening test
            record_category = 'Screening Test' if category == 'screening' else category
            
            # Save answer using database manager
            print(f"Saving answer: user_id={user_id}, question_id={question_id}, category={record_category}, selected_answer={selected_answer}, is_correct={is_correct}")
            
            result = db_manager.save_user_answer(
                user_id=user_id,
                question_id=question_id,
                category=record_category,
                selected_answer=selected_answer,
                is_correct=is_correct
            )
            print(f"Save result: {result}")
            
            # Get updated stats
            stats = db_manager.get_category_stats(user_id, record_category)
            
            return jsonify({
                'correct': is_correct,
                'correct_answer': correct_answer,
                'explanation': None,  # Will be requested separately if needed
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/hint', methods=['POST'])
def get_hint():
    """Get hint for a question"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        
        if not question_id:
            return jsonify({'error': 'Question ID required'}), 400
        
        # Get question from database
        from utils.database import Question
        db = db_manager.get_db()
        try:
            question = db.query(Question).filter(
                Question.id == question_id
            ).first()
            
            if not question:
                return jsonify({'error': 'Question not found'}), 404
            
            hint = question.hint or "Подсказка для этого вопроса не добавлена"
            
            return jsonify({
                'hint': hint
            })
        finally:
            db.close()
            
    except Exception as e:
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
            import hashlib
            browser_fingerprint = request.headers.get('User-Agent', '') + str(request.remote_addr)
            session_key = session.get('_permanent_session_key')
            if not session_key:
                session_key = hashlib.md5(browser_fingerprint.encode()).hexdigest()[:12]
                session['_permanent_session_key'] = session_key
            
            user_id = f"guest_{session_key}"
            session['user_id'] = user_id
            session.permanent = True
            print(f"Created persistent guest user_id for test completion: {user_id}")
        
        # Try to save first test result
        first_time = db_manager.save_first_test_result(user_id, category, subcategory, score, total_questions)
        
        # Get social comparison statistics
        social_stats = db_manager.get_test_social_stats(category, subcategory, score)
        
        return jsonify({
            'first_time': first_time,
            'social_stats': social_stats
        })
        
    except Exception as e:
        print(f"Error completing test: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/start', methods=['POST'])
def start_ai_chat():
    """Start AI chat session for a question"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        
        if not question_id:
            return jsonify({'error': 'Question ID required'}), 400
        
        # Get question from database
        from utils.database import Question
        db = db_manager.get_db()
        try:
            question = db.query(Question).filter(
                Question.id == question_id
            ).first()
            
            if not question:
                return jsonify({'error': 'Question not found'}), 404
            
            options = json.loads(question.options)
            
            # Initialize chat session
            chat_id = f"chat_{question_id}_{session.get('user_id', 'anonymous')}"
            
            # Store chat context in session
            if 'ai_chats' not in session:
                session['ai_chats'] = {}
            
            session['ai_chats'][chat_id] = {
                'question': question.question_text,
                'options': options,
                'correct_answer': question.correct_answer,
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
            
            # Make session permanent to persist chats
            session.permanent = True
            
            # Initial AI response with better formatting
            formatted_question = question.question_text.replace('```', '\n---\n')
            formatted_options = '\n'.join([f"• {opt}" for opt in options])
            
            initial_message = f"""🤖 Привет! Я готов помочь разобраться с этим вопросом:

📝 ВОПРОС:
{formatted_question}

📋 ВАРИАНТЫ ОТВЕТА:
{formatted_options}

💡 Что именно тебя интересует? Можешь задать любой уточняющий вопрос!"""
            
            session['ai_chats'][chat_id]['messages'].append({
                'role': 'assistant',
                'content': initial_message
            })
            
            return jsonify({
                'chat_id': chat_id,
                'message': initial_message
            })
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/message', methods=['POST'])
def send_chat_message():
    """Send message to AI chat"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        user_message = data.get('message')
        
        if not all([chat_id, user_message]):
            return jsonify({'error': 'Chat ID and message required'}), 400
        
        # Get chat context
        if 'ai_chats' not in session:
            session['ai_chats'] = {}
        
        if chat_id not in session['ai_chats']:
            return jsonify({'error': 'Chat session not found. Please start a new chat.'}), 404
        
        chat_context = session['ai_chats'][chat_id]
        
        # Add user message to context
        chat_context['messages'].append({
            'role': 'user',
            'content': user_message
        })
        
        # Create context for AI
        context = f"""Вопрос: {chat_context['question']}
Варианты: {', '.join(chat_context['options'])}
Правильный ответ: {chat_context['correct_answer']}

История беседы:
{chr(10).join([f"{msg['role']}: {msg['content']}" for msg in chat_context['messages'][-5:]])}

Пользователь спрашивает: {user_message}

НЕ используй пронумерованные списки или формальную структуру!
Отвечай как опытный программист-друг, который объясняет понятно и интересно."""
        
        # Get AI response
        from utils.yandex_gpt_helper import explain_concept
        ai_response = explain_concept(user_message, context)
        
        # Add AI response to context
        chat_context['messages'].append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # Save updated context and ensure session is permanent
        session['ai_chats'][chat_id] = chat_context
        session.permanent = True
        session.modified = True
        
        return jsonify({
            'message': ai_response
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress')
def get_progress():
    """Get user's detailed progress"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Create persistent user_id based on browser session
            import hashlib
            browser_fingerprint = request.headers.get('User-Agent', '') + str(request.remote_addr)
            session_key = session.get('_permanent_session_key')
            if not session_key:
                session_key = hashlib.md5(browser_fingerprint.encode()).hexdigest()[:12]
                session['_permanent_session_key'] = session_key
            
            user_id = f"guest_{session_key}"
            session['user_id'] = user_id
            session.permanent = True
            print(f"Created persistent guest user_id: {user_id}")
        
        # Use the database manager directly instead of progress tracker
        overall_progress = db_manager.get_user_progress(user_id)
        
        # Get overall statistics
        overall_score = overall_progress.get('overall_score', 0.0)
        total_answered = overall_progress.get('total_answered', 0)
        
        # Determine overall level
        if overall_score >= 80:
            overall_level = "Senior"
            level_emoji = "🏆"
        elif overall_score >= 60:
            overall_level = "Middle"
            level_emoji = "🥈"
        else:
            overall_level = "Junior"
            level_emoji = "🥉"
        
        # Get category progress
        categories = db_manager.get_all_categories()
        category_progress = []
        
        for category in categories:
            stats = db_manager.get_category_stats(user_id, category)
            if stats['total'] > 0:
                category_progress.append({
                    'category': category,
                    'total': stats['total'],
                    'correct': stats['correct'],
                    'score': stats['score'],
                    'level': stats.get('level', 'Junior')
                })
        
        print(f"Category progress for user {user_id}: {category_progress}")
        print(f"Overall progress data: {overall_progress}")
        
        # Get recent performance (using simpler approach)
        recent_answers = db_manager.get_recent_answers(user_id, 10)
        print(f"Recent answers: {recent_answers}")
        
        # Calculate weak and strong areas from category progress
        weak_areas = [cat for cat in category_progress if cat['score'] < 60]
        strong_areas = [cat for cat in category_progress if cat['score'] >= 80]
        
        return jsonify({
            'overall_score': overall_score,
            'overall_level': overall_level,
            'level_emoji': level_emoji,
            'total_answered': total_answered,
            'categories': category_progress,
            'recent_answers': recent_answers,
            'weak_areas': weak_areas,
            'strong_areas': strong_areas
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get AI-powered recommendations"""
    try:
        user_id = session.get('user_id')
        progress_tracker = DatabaseProgressTracker(user_id)
        
        weak_areas = progress_tracker.get_weak_areas()
        overall_score = progress_tracker.get_overall_score()
        total_answered = progress_tracker.get_total_questions_answered()
        
        if total_answered < 5:
            return jsonify({
                'recommendations': 'Пройдите больше тестов для получения персонализированных рекомендаций!'
            })
        
        user_progress = {
            'total_questions': total_answered,
            'overall_score': overall_score,
            'weak_areas': weak_areas
        }
        
        recommendations = get_personalized_recommendations(user_progress, weak_areas)
        
        return jsonify({
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard')
def get_leaderboard():
    """Get leaderboard (top users by score)"""
    try:
        # This would require additional database queries to get top users
        # For now, return a placeholder
        return jsonify({
            'leaderboard': [
                {'username': 'Anonymous User', 'score': 95.5, 'level': 'Senior'},
                {'username': 'You', 'score': session.get('user_score', 0), 'level': 'Junior'}
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile')
def get_user_profile():
    """Get user profile information"""
    try:
        user_id = session.get('user_id')
        
        # If no user_id in session, create a guest user
        if not user_id:
            user_id = db_manager.get_or_create_user(session_id=str(uuid.uuid4()))
            session['user_id'] = user_id
            session['auth_type'] = 'guest'
        
        profile = db_manager.get_user_profile(user_id)
        
        # If profile still not found, create a basic profile structure
        if not profile:
            profile = {
                'id': user_id,
                'telegram_id': None,
                'telegram_username': None,
                'telegram_first_name': None,
                'telegram_last_name': None,
                'created_at': datetime.utcnow().isoformat(),
                'last_active': datetime.utcnow().isoformat()
            }
        
        # Add auth type from session
        auth_type = session.get('auth_type', 'guest')
        profile['auth_type'] = auth_type
        
        # Create display name
        if profile.get('telegram_first_name'):
            display_name = profile['telegram_first_name']
            if profile.get('telegram_last_name'):
                display_name += ' ' + profile['telegram_last_name']
            profile['display_name'] = display_name
        elif profile.get('telegram_username'):
            profile['display_name'] = profile['telegram_username']
        else:
            profile['display_name'] = 'Пользователь'
        
        return jsonify(profile)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database tables on startup
    try:
        db_manager.create_tables()
        print("✓ Таблицы базы данных созданы/проверены")
        
        # Load initial questions if database is empty
        try:
            categories = db_manager.get_all_categories()
            if not categories:
                import json
                with open('data/questions.json', 'r', encoding='utf-8') as f:
                    questions_data = json.load(f)
                db_manager.load_questions_to_db(questions_data)
                print("✓ Начальные вопросы загружены в базу данных")
        except Exception as e:
            print(f"⚠ Ошибка загрузки вопросов: {e}")
            
    except Exception as e:
        print(f"✗ Ошибка инициализации базы данных: {e}")

# Premium access functions
def check_user_premium(user_id):
    """Check if user has premium access"""
    try:
        # For demo purposes, guest users don't have premium
        if user_id and user_id.startswith('guest_'):
            return False
        
        # Check premium status in session (simplified for demo)
        premium_users = session.get('premium_users', set())
        return user_id in premium_users
    except Exception as e:
        print(f"Error checking premium status: {e}")
        return False

def grant_premium_access(user_id):
    """Grant premium access to user after successful payment"""
    try:
        premium_users = session.get('premium_users', set())
        premium_users.add(user_id)
        session['premium_users'] = premium_users
        session.permanent = True
        print(f"Premium access granted to user: {user_id}")
        return True
    except Exception as e:
        print(f"Error granting premium access: {e}")
        return False

# Payment endpoints
@app.route('/api/create_invoice', methods=['POST'])
def create_invoice():
    """Create Telegram invoice for premium access"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Create invoice payload for Telegram Payments
        invoice_payload = {
            "title": "Interview Prep Premium",
            "description": "Доступ ко всем премиум модулям: ML, NLP, Computer Vision, Deep Learning",
            "payload": f"premium_access_{user_id}",
            "provider_token": "",  # Use test token or real payment provider
            "currency": "RUB",
            "prices": [{"label": "Premium доступ", "amount": 49900}],  # 499 RUB in kopecks
            "need_email": False,
            "need_phone_number": False,
            "need_shipping_address": False,
            "is_flexible": False
        }
        
        return jsonify({
            'status': 'success',
            'invoice': invoice_payload,
            'message': 'Инвойс создан успешно'
        })
        
    except Exception as e:
        print(f"Error creating invoice: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process_payment', methods=['POST'])
def process_payment():
    """Process successful payment and grant premium access"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # In real implementation, verify payment with Telegram
        # For demo, we'll grant access immediately
        success = grant_premium_access(user_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Премиум доступ активирован!',
                'premium': True
            })
        else:
            return jsonify({'error': 'Failed to activate premium'}), 500
            
    except Exception as e:
        print(f"Error processing payment: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=config.get('app.debug', True), 
            host=config.get('app.host', '0.0.0.0'), 
            port=config.get('app.main_port', 5000))
