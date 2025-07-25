import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from utils.database import db_manager, Question
from werkzeug.security import check_password_hash, generate_password_hash
from config_loader import config
import uuid

app = Flask(__name__)
app.secret_key = config.get('admin.secret_key', 'admin-secret-key')

# Upload configuration
UPLOAD_FOLDER = 'static/images/questions'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple admin authentication
ADMIN_PASSWORD = config.get('admin.password', 'admin123')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/admin')
def admin_login():
    """Admin login page"""
    return render_template('admin_login.html')

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    """Authenticate admin user"""
    password = request.form.get('password')
    if password == ADMIN_PASSWORD:
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Неверный пароль')
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    try:
        categories = db_manager.get_all_categories()
        stats = {}
        
        for category in categories:
            questions = db_manager.get_questions_by_category(category)
            stats[category] = {
                'total': len(questions),
                'with_hints': sum(1 for q in questions if q.get('hint')),
                'verified': sum(1 for q in questions if q.get('verified', False))
            }
        
        return render_template('admin_dashboard.html', categories=categories, stats=stats)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_login'))

@app.route('/admin/subcategories')
def admin_subcategories():
    """Manage subcategories"""
    try:
        categories = db_manager.get_all_categories()
        
        # Get subcategories for each category
        subcategory_data = {}
        for category in categories:
            subcategories = db_manager.get_subcategories_by_category(category)
            subcategory_data[category] = subcategories
        
        return render_template('admin_subcategories.html', 
                             categories=categories, 
                             subcategory_data=subcategory_data)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_subcategory_question', methods=['GET', 'POST'])
def admin_add_subcategory_question():
    """Add question with subcategory"""
    if request.method == 'POST':
        try:
            category = request.form.get('category')
            sub_category = request.form.get('sub_category')
            question_text = request.form.get('question_text')
            options = [
                request.form.get('option1'),
                request.form.get('option2'),
                request.form.get('option3'),
                request.form.get('option4')
            ]
            correct_answer = request.form.get('correct_answer')
            hint = request.form.get('hint')
            
            if not all([category, sub_category, question_text, correct_answer]):
                flash('Заполните все обязательные поля')
                return redirect(url_for('admin_add_subcategory_question'))
            
            # Validate that correct_answer is one of the options
            if correct_answer not in options:
                flash('Правильный ответ должен быть одним из вариантов')
                return redirect(url_for('admin_add_subcategory_question'))
            
            question_id = db_manager.create_question_with_subcategory(
                category=category,
                sub_category=sub_category,
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                hint=hint
            )
            
            flash(f'Вопрос добавлен успешно (ID: {question_id})')
            return redirect(url_for('admin_add_subcategory_question'))
            
        except Exception as e:
            flash(f'Ошибка при добавлении вопроса: {str(e)}')
            return redirect(url_for('admin_add_subcategory_question'))
    
    # GET request - show form
    try:
        categories = db_manager.get_all_categories()
        return render_template('admin_add_subcategory_question.html', categories=categories)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_image_question', methods=['GET', 'POST'])
def admin_add_image_question():
    """Add question with image"""
    if request.method == 'POST':
        try:
            category = request.form.get('category')
            sub_category = request.form.get('sub_category')
            question_text = request.form.get('question_text')
            options = [
                request.form.get('option1'),
                request.form.get('option2'),
                request.form.get('option3'),
                request.form.get('option4')
            ]
            correct_answer = request.form.get('correct_answer')
            hint = request.form.get('hint')
            
            if not all([category, sub_category, question_text, correct_answer]):
                flash('Заполните все обязательные поля')
                return redirect(url_for('admin_add_image_question'))
            
            # Validate that correct_answer is one of the options
            if correct_answer not in options:
                flash('Правильный ответ должен быть одним из вариантов')
                return redirect(url_for('admin_add_image_question'))
            
            # Handle file upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Generate unique filename
                    file_extension = file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"question_{uuid.uuid4().hex}.{file_extension}"
                    
                    # Save file
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    image_path = f"images/questions/{unique_filename}"
                    
            question_id = db_manager.add_question_with_image(
                category=category,
                sub_category=sub_category,
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                hint=hint,
                image_path=image_path
            )
            
            flash(f'Вопрос с изображением добавлен успешно (ID: {question_id})')
            return redirect(url_for('admin_add_image_question'))
            
        except Exception as e:
            flash(f'Ошибка при добавлении вопроса: {str(e)}')
            return redirect(url_for('admin_add_image_question'))
    
    # GET request - show form
    try:
        categories = db_manager.get_all_categories()
        return render_template('admin_add_image_question.html', categories=categories)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/static/<path:filename>')
def admin_uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory('static', filename)



@app.route('/admin/database')
def admin_database():
    """Database viewer"""
    try:
        import sqlite3
        
        # Подключаемся к базе данных
        conn = sqlite3.connect('interview_prep.db')
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Получаем статистику по каждой таблице
        table_stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            
            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            
            table_stats[table] = {
                'count': count,
                'columns': [(col[1], col[2]) for col in columns]
            }
        
        conn.close()
        
        return render_template('admin_database.html', tables=table_stats)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/api/modules')
def api_modules():
    """Get modules for admin panel"""
    try:
        modules = db_manager.get_all_modules()
        return jsonify(modules)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/modules', methods=['POST'])
def create_module():
    """Create new module"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        display_name = data.get('display_name', '').strip()
        description = data.get('description', '').strip()
        icon = data.get('icon', '📚').strip()
        is_premium = data.get('is_premium', False)
        price = data.get('price', 0.0)
        
        if not name:
            return jsonify({'error': 'Название модуля обязательно'}), 400
        
        # Create module in database
        module_id = db_manager.create_module(
            name=name,
            display_name=display_name or name,
            description=description or f"Модуль {name}",
            icon=icon,
            is_premium=is_premium,
            price=price
        )
        
        if module_id:
            return jsonify({'success': True, 'message': 'Модуль создан успешно', 'module_id': module_id})
        else:
            return jsonify({'error': 'Не удалось создать модуль'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/modules/<int:module_id>/premium', methods=['POST'])
def update_module_premium(module_id):
    """Update module premium status"""
    try:
        data = request.get_json()
        is_premium = data.get('is_premium', False)
        price = data.get('price', 0.0)
        
        success = db_manager.update_module_premium_status(module_id, is_premium, price)
        
        if success:
            return jsonify({'success': True, 'message': 'Статус модуля обновлен'})
        else:
            return jsonify({'error': 'Не удалось обновить модуль'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/admin/table/<table_name>')
def admin_table_data(table_name):
    """View table data"""
    try:
        # Проверяем безопасность имени таблицы
        allowed_tables = ['users', 'questions', 'user_answers', 'user_progress', 'modules']
        if table_name not in allowed_tables:
            flash('Недопустимое имя таблицы')
            return redirect(url_for('admin_database'))
        
        # Получаем данные через DatabaseManager
        if table_name == 'modules':
            data = db_manager.get_all_modules()
            columns = ['id', 'name', 'display_name', 'description', 'icon', 'is_premium', 'price']
            rows = [[m.get(col, '') for col in columns] for m in data]
        elif table_name == 'questions':
            data = db_manager.get_all_questions()
            columns = ['id', 'category', 'sub_category', 'question_text', 'correct_answer']
            rows = [[q.get(col, '') for col in columns] for q in data[:50]]  # Limit to 50
        else:
            # Fallback for other tables
            columns = []
            rows = []
        
        # Расчет пагинации
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('admin_table_data.html', 
                             table_name=table_name,
                             columns=columns, 
                             rows=rows,
                             page=page,
                             total_pages=total_pages,
                             total_count=total_count)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_database'))

@app.route('/admin/category/<category>')
def admin_category(category):
    """Admin category management"""
    try:
        questions = db_manager.get_questions_by_category(category)
        return render_template('admin_category.html', category=category, questions=questions)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/question/<int:question_id>')
def admin_question(question_id):
    """Admin question editing"""
    try:
        db = db_manager.get_db()
        question = db.query(Question).filter(Question.id == question_id).first()
        db.close()
        
        if not question:
            flash('Вопрос не найден')
            return redirect(url_for('admin_dashboard'))
        
        # Parse JSON options
        options = json.loads(question.options) if question.options else []
        
        return render_template('admin_question.html', 
                             question=question, 
                             options=options)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/question/<int:question_id>/save', methods=['POST'])
def admin_save_question(question_id):
    """Save question updates"""
    db = None
    try:
        db = db_manager.get_db()
        question = db.query(Question).filter(Question.id == question_id).first()
        
        if not question:
            flash('Вопрос не найден')
            return redirect(url_for('admin_dashboard'))
        
        # Store category before modifying
        category = question.category
        
        # Update question fields
        question.question_text = request.form.get('question_text', '').strip()
        question.correct_answer = request.form.get('correct_answer', '').strip()
        question.hint = request.form.get('hint', '').strip()
        question.verified = request.form.get('verified') == 'on'
        
        # Update options
        options = []
        for i in range(1, 5):  # Assuming max 4 options
            option = request.form.get(f'option_{i}', '').strip()
            if option:
                options.append(option)
        
        question.options = json.dumps(options)
        
        # Validate that correct answer is in options
        if question.correct_answer not in options:
            flash('Правильный ответ должен быть одним из вариантов!')
            return redirect(url_for('admin_question', question_id=question_id))
        
        db.commit()
        flash('Вопрос успешно обновлен!')
        return redirect(url_for('admin_category', category=category))
        
    except Exception as e:
        if db:
            db.rollback()
        flash(f'Ошибка при сохранении: {str(e)}')
        return redirect(url_for('admin_question', question_id=question_id))
    finally:
        if db:
            db.close()

@app.route('/admin/question/new/<category>')
def admin_new_question(category):
    """Create new question"""
    return render_template('admin_new_question.html', category=category)



@app.route('/admin/api/stats')
def admin_api_stats():
    """API endpoint for admin stats"""
    try:
        categories = db_manager.get_all_categories()
        total_questions = 0
        verified_questions = 0
        questions_with_hints = 0
        
        for category in categories:
            questions = db_manager.get_questions_by_category(category)
            total_questions += len(questions)
            verified_questions += sum(1 for q in questions if q.get('verified', False))
            questions_with_hints += sum(1 for q in questions if q.get('hint'))
        
        return jsonify({
            'total_questions': total_questions,
            'verified_questions': verified_questions,
            'questions_with_hints': questions_with_hints,
            'categories_count': len(categories)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/add_question')
def admin_add_question():
    """Add new question form"""
    try:
        categories = db_manager.get_all_categories()
        return render_template('admin_add_question.html', categories=categories)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_question', methods=['POST'])
def admin_create_new_question():
    """Save new question"""
    try:
        category = request.form.get('category')
        new_category = request.form.get('new_category')
        question_text = request.form.get('question_text')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_answer = request.form.get('correct_answer')
        hint = request.form.get('hint')
        
        # Use new category if provided
        if new_category:
            category = new_category.strip()
        
        # Validate required fields
        if not all([category, question_text, option1, option2, option3, option4, correct_answer]):
            flash('Все поля обязательны для заполнения')
            return redirect(url_for('admin_add_question'))
        
        # Create options list
        options = [option1, option2, option3, option4]
        
        # Validate that correct answer is one of the options
        if correct_answer not in options:
            flash('Правильный ответ должен совпадать с одним из вариантов')
            return redirect(url_for('admin_add_question'))
        
        # Save question to database
        from utils.database import Question
        import json
        
        db = db_manager.get_db()
        try:
            new_question = Question(
                category=category,
                question_text=question_text,
                options=json.dumps(options, ensure_ascii=False),
                correct_answer=correct_answer,
                hint=hint if hint else None,
                verified=False
            )
            
            db.add(new_question)
            db.commit()
            
            flash(f'Вопрос успешно добавлен в категорию "{category}"')
            return redirect(url_for('admin_dashboard'))
        finally:
            db.close()
            
    except Exception as e:
        flash(f'Ошибка при сохранении вопроса: {str(e)}')
        return redirect(url_for('admin_add_question'))

# Module and Submodule Management Routes
@app.route('/admin/modules', methods=['GET', 'POST'])
def admin_modules():
    """Module management page with premium toggle functionality"""
    if request.method == 'POST':
        try:
            module_id = int(request.form.get('module_id'))
            is_premium = 'is_premium' in request.form
            price = float(request.form.get('price', 0.0)) if is_premium else 0.0
            
            success = db_manager.update_module_premium_status(module_id, is_premium, price)
            
            if success:
                flash('Модуль обновлен успешно')
            else:
                flash('Ошибка при обновлении модуля')
                
        except Exception as e:
            flash(f'Ошибка: {str(e)}')
        
        return redirect(url_for('admin_modules'))
    
    # GET request - show modules
    try:
        modules = db_manager.get_all_modules()
        return render_template('admin_modules.html', modules=modules)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/api/modules/<int:module_id>/premium', methods=['POST'])
def update_module_premium_status(module_id):
    """API endpoint to update module premium status"""
    try:
        data = request.get_json()
        is_premium = data.get('is_premium', False)
        price = data.get('price', 0.0)
        
        success = db_manager.update_module_premium_status(module_id, is_premium, price)
        
        if success:
            return jsonify({'success': True, 'message': 'Модуль обновлен успешно'})
        else:
            return jsonify({'success': False, 'error': 'Ошибка при обновлении модуля'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/modules', methods=['POST'])
def create_module_api():
    """API endpoint to create new module"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        display_name = data.get('display_name', '').strip() or name
        description = data.get('description', '').strip()
        icon = data.get('icon', '📚').strip()
        is_premium = data.get('is_premium', False)
        price = data.get('price', 0.0)
        
        if not name:
            return jsonify({'success': False, 'error': 'Название модуля обязательно'})
        
        module_id = db_manager.create_module(name, description, icon, is_premium, price)
        
        if module_id:
            return jsonify({'success': True, 'message': 'Модуль создан успешно', 'module_id': module_id})
        else:
            return jsonify({'success': False, 'error': 'Ошибка при создании модуля'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/create_module', methods=['POST'])
def admin_create_module():
    """Create new module"""
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', '').strip()
        color = request.form.get('color', '').strip()
        
        if not name:
            flash('Название модуля обязательно')
            return redirect(url_for('admin_modules'))
        
        db_manager.create_module(name, description, icon, color)
        flash(f'Модуль "{name}" успешно создан')
        return redirect(url_for('admin_modules'))
        
    except Exception as e:
        flash(f'Ошибка при создании модуля: {str(e)}')
        return redirect(url_for('admin_modules'))

@app.route('/admin/create_submodule', methods=['POST'])
def admin_create_submodule():
    """Create new submodule"""
    try:
        module_id = request.form.get('module_id')
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', '').strip()
        difficulty = request.form.get('difficulty', '').strip()
        
        if not all([module_id, name]):
            flash('Модуль и название подмодуля обязательны')
            return redirect(url_for('admin_modules'))
        
        db_manager.create_submodule(int(module_id), name, description, icon, difficulty)
        flash(f'Подмодуль "{name}" успешно создан')
        return redirect(url_for('admin_modules'))
        
    except Exception as e:
        flash(f'Ошибка при создании подмодуля: {str(e)}')
        return redirect(url_for('admin_modules'))

@app.route('/admin/submodule/<int:submodule_id>/add_question')
def admin_add_submodule_question(submodule_id):
    """Add question to submodule form"""
    try:
        submodule = db_manager.get_submodule_by_id(submodule_id)
        if not submodule:
            flash('Подмодуль не найден')
            return redirect(url_for('admin_modules'))
        
        return render_template('admin_add_submodule_question.html', submodule=submodule)
    except Exception as e:
        flash(f'Ошибка: {str(e)}')
        return redirect(url_for('admin_modules'))

@app.route('/admin/create_submodule_question', methods=['POST'])
def admin_create_submodule_question():
    """Save new question to submodule"""
    try:
        submodule_id = request.form.get('submodule_id')
        question_text = request.form.get('question_text', '').strip()
        option1 = request.form.get('option1', '').strip()
        option2 = request.form.get('option2', '').strip()
        option3 = request.form.get('option3', '').strip()
        option4 = request.form.get('option4', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        hint = request.form.get('hint', '').strip()
        
        if not all([submodule_id, question_text, option1, option2, option3, option4, correct_answer]):
            flash('Все поля обязательны для заполнения')
            return redirect(url_for('admin_add_submodule_question', submodule_id=submodule_id))
        
        options = [option1, option2, option3, option4]
        if correct_answer not in options:
            flash('Правильный ответ должен совпадать с одним из вариантов')
            return redirect(url_for('admin_add_submodule_question', submodule_id=submodule_id))
        
        # Get submodule info for category
        submodule = db_manager.get_submodule_by_id(int(submodule_id))
        category = submodule['module']['name'] if submodule.get('module') else 'General'
        
        # Create question
        from utils.database import Question
        import json
        
        db = db_manager.get_db()
        try:
            new_question = Question(
                category=category,  # For backward compatibility
                submodule_id=int(submodule_id),
                question_text=question_text,
                options=json.dumps(options, ensure_ascii=False),
                correct_answer=correct_answer,
                hint=hint if hint else None,
                verified=True
            )
            
            db.add(new_question)
            db.commit()
            
            flash(f'Вопрос успешно добавлен в подмодуль "{submodule["name"]}"')
            return redirect(url_for('admin_modules'))
        finally:
            db.close()
            
    except Exception as e:
        flash(f'Ошибка при сохранении вопроса: {str(e)}')
        return redirect(url_for('admin_modules'))

if __name__ == '__main__':
    app.run(debug=config.get('app.debug', True), 
            host=config.get('app.host', '0.0.0.0'), 
            port=config.get('app.admin_port', 5001))