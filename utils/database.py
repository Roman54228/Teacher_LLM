import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
import sys

# Import config loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config_loader import config
    DATABASE_URL = config.get_database_url()
    print(f"✓ Подключение к базе данных: {DATABASE_URL.split('://')[0]}://...")
except Exception as e:
    print(f"⚠ Ошибка загрузки конфигурации: {e}")
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///interview_prep.db")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True, nullable=True)
    telegram_id = Column(String, index=True, nullable=True)
    telegram_username = Column(String, nullable=True)
    telegram_first_name = Column(String, nullable=True)
    telegram_last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # Main category (Python, ML, etc.)
    sub_category = Column(String, nullable=True)  # Sub-category within main category
    submodule_id = Column(Integer, nullable=True)  # References submodules.id (legacy)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON string
    correct_answer = Column(String, nullable=False)
    hint = Column(Text, nullable=True)  # Hint for the question
    image_path = Column(String, nullable=True)  # Path to question image
    verified = Column(Boolean, default=False)  # Admin verification flag
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAnswer(Base):
    __tablename__ = "user_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    question_id = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    selected_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow)

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    level = Column(String, default="Junior")
    last_updated = Column(DateTime, default=datetime.utcnow)

class FirstTestResult(Base):
    __tablename__ = "first_test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    category = Column(String, nullable=False)  # Main category (Python, ML, etc.)
    subcategory = Column(String, nullable=False)  # Subcategory within main category
    score = Column(Integer, nullable=False)  # Number of correct answers
    total_questions = Column(Integer, nullable=False)  # Total questions in test
    score_percentage = Column(Float, nullable=False)  # Percentage score
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Add unique constraint to ensure only one first result per user per test
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Submodule(Base):
    __tablename__ = "submodules"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, nullable=False)  # References modules.id
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)  # Beginner, Intermediate, Advanced
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database Manager Class
class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
        # Set db_path for SQLite operations
        if 'sqlite' in DATABASE_URL:
            self.db_path = DATABASE_URL.replace('sqlite:///', '').replace('sqlite://', '')
            if not self.db_path.startswith('/'):
                self.db_path = os.path.join(os.getcwd(), self.db_path)
        else:
            self.db_path = 'interview_prep.db'  # fallback
        
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_db(self):
        """Get database session"""
        db = self.SessionLocal()
        try:
            return db
        finally:
            pass  # Don't close here, let the caller handle it
    
    def get_or_create_user(self, session_id: str = None, telegram_id: str = None, telegram_data: dict = None) -> str:
        """Get or create user by session ID or Telegram ID"""
        db = self.get_db()
        try:
            user = None
            
            # Try to find user by Telegram ID first
            if telegram_id:
                user = db.query(User).filter(User.telegram_id == telegram_id).first()
                
                if user:
                    # Update Telegram data if provided
                    if telegram_data:
                        user.telegram_username = telegram_data.get('username')
                        user.telegram_first_name = telegram_data.get('first_name')
                        user.telegram_last_name = telegram_data.get('last_name')
                    
                    # Update session ID if provided
                    if session_id and user.session_id != session_id:
                        user.session_id = session_id
                    
                    user.last_active = datetime.utcnow()
                    db.commit()
                    return user.id
            
            # Try to find by session ID if Telegram ID not found
            if session_id:
                user = db.query(User).filter(User.session_id == session_id).first()
                
                if user and telegram_id:
                    # Link Telegram account to existing session user
                    user.telegram_id = telegram_id
                    if telegram_data:
                        user.telegram_username = telegram_data.get('username')
                        user.telegram_first_name = telegram_data.get('first_name')
                        user.telegram_last_name = telegram_data.get('last_name')
                    user.last_active = datetime.utcnow()
                    db.commit()
                    return user.id
            
            # Create new user if not found
            if not user:
                user_data = {}
                if session_id:
                    user_data['session_id'] = session_id
                if telegram_id:
                    user_data['telegram_id'] = telegram_id
                if telegram_data:
                    user_data.update({
                        'telegram_username': telegram_data.get('username'),
                        'telegram_first_name': telegram_data.get('first_name'),
                        'telegram_last_name': telegram_data.get('last_name')
                    })
                
                user = User(**user_data)
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                # Update last active time for existing user
                user.last_active = datetime.utcnow()
                db.commit()
            
            return user.id
        finally:
            db.close()
    
    def load_questions_to_db(self, questions_data: Dict):
        """Load questions from JSON data to database"""
        db = self.get_db()
        count = 0
        try:
            for category, category_data in questions_data.items():
                # Check if category_data is a dict (with subcategories) or list (direct questions)
                if isinstance(category_data, dict):
                    # New format: category -> subcategory -> questions
                    for subcategory, questions in category_data.items():
                        for q_data in questions:
                            question = Question(
                                category=category,
                                sub_category=subcategory,
                                question_text=q_data['question'],
                                options=json.dumps(q_data['options']),
                                correct_answer=q_data['correct_answer'],
                                hint=q_data.get('hint')
                            )
                            db.add(question)
                            count += 1
                else:
                    # Legacy format: category -> questions (direct list)
                    for q_data in category_data:
                        question = Question(
                            category=category,
                            sub_category=q_data.get('sub_category'),
                            question_text=q_data['question'],
                            options=json.dumps(q_data['options']),
                            correct_answer=q_data['correct_answer'],
                            hint=q_data.get('hint'),
                            verified=q_data.get('verified', True)
                        )
                        db.add(question)
                        count += 1
            
            db.commit()
            return count
        finally:
            db.close()
    
    def get_questions_by_category(self, category: str) -> List[Dict]:
        """Get all questions for a specific category"""
        db = self.get_db()
        try:
            questions = db.query(Question).filter(Question.category == category).all()
            result = []
            for q in questions:
                result.append({
                    'id': q.id,
                    'question': q.question_text,
                    'options': json.loads(q.options),
                    'correct_answer': q.correct_answer,
                    'hint': getattr(q, 'hint', None),
                    'image_path': getattr(q, 'image_path', None),
                    'verified': getattr(q, 'verified', False)
                })
            return result
        finally:
            db.close()
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        db = self.get_db()
        try:
            categories = db.query(Question.category).distinct().all()
            return [cat[0] for cat in categories]
        finally:
            db.close()
    
    def get_subcategories_by_category(self, category: str) -> List[str]:
        """Get all subcategories for a specific category"""
        db = self.get_db()
        try:
            subcategories = db.query(Question.sub_category).filter(
                Question.category == category,
                Question.sub_category.isnot(None),
                Question.sub_category != '',
                Question.sub_category != ' '
            ).distinct().all()
            result = [subcat[0].strip() for subcat in subcategories if subcat[0] and subcat[0].strip()]
            print(f"DEBUG: Found subcategories for {category}: {result}")
            return result
        finally:
            db.close()
    
    def get_questions_by_subcategory(self, category: str, sub_category: str) -> List[Dict]:
        """Get all questions for a specific subcategory"""
        db = self.get_db()
        try:
            # Clean up input parameters
            category = category.strip()
            sub_category = sub_category.strip()
            
            print(f"DEBUG: Searching for category='{category}', sub_category='{sub_category}'")
            
            # Try exact match first
            questions = db.query(Question).filter(
                Question.category == category,
                Question.sub_category == sub_category
            ).all()
            
            # If no exact match, try to find all questions for this category and debug
            if not questions:
                print(f"DEBUG: No exact match, trying to find any questions for category '{category}'")
                all_questions_in_category = db.query(Question).filter(
                    Question.category == category
                ).all()
                print(f"DEBUG: Found {len(all_questions_in_category)} questions in category")
                for q in all_questions_in_category[:3]:  # Show first 3
                    print(f"DEBUG: Question {q.id}: category='{q.category}', sub_category='{q.sub_category}' (type: {type(q.sub_category)})")
                    
                # Since sub_category is None, let's just return all questions for this category
                if sub_category == 'Обработка изображений' and all_questions_in_category:
                    print(f"DEBUG: Using all questions from category as fallback")
                    questions = all_questions_in_category
                else:
                    # Try case-insensitive search
                    questions = db.query(Question).filter(
                        Question.category.ilike(f'%{category}%'),
                        Question.sub_category.ilike(f'%{sub_category}%')
                    ).all()
            
            print(f"DEBUG: Found {len(questions)} questions")
            
            result = []
            for q in questions:
                result.append({
                    'id': q.id,
                    'question': q.question_text,
                    'options': json.loads(q.options),
                    'correct_answers': [q.correct_answer],  # Make it a list for consistency
                    'correct_answer': q.correct_answer,
                    'hint': getattr(q, 'hint', None),
                    'image_path': getattr(q, 'image_path', None),
                    'verified': getattr(q, 'verified', False),
                    'sub_category': q.sub_category
                })
            return result
        finally:
            db.close()

    def get_question_by_id(self, question_id: int) -> Dict:
        """Get single question by ID"""
        db = self.get_db()
        try:
            q = db.query(Question).filter(Question.id == question_id).first()
            if not q:
                return None
            
            return {
                'id': q.id,
                'category': q.category,
                'subcategory': getattr(q, 'sub_category', ''),
                'question': q.question_text,
                'options': json.loads(q.options),
                'correct_answers': [q.correct_answer],  # Make it a list for consistency
                'correct_answer': q.correct_answer,
                'hint': getattr(q, 'hint', None),
                'image_path': getattr(q, 'image_path', None),
                'verified': getattr(q, 'verified', False)
            }
        finally:
            db.close()
    
    def save_user_answer(self, session_id: str, question_id: int, user_answer: str, 
                        is_correct: bool, category: str = None, subcategory: str = None):
        """Save user answer to database"""
        db = self.get_db()
        try:
            # Check if answer already exists
            existing = db.query(UserAnswer).filter(
                UserAnswer.session_id == session_id,
                UserAnswer.question_id == question_id
            ).first()
            
            if existing:
                # Update existing answer
                existing.user_answer = user_answer
                existing.is_correct = is_correct
                existing.answered_at = datetime.utcnow()
            else:
                # Create new answer record
                user_answer_record = UserAnswer(
                    session_id=session_id,
                    question_id=question_id,
                    user_answer=user_answer,
                    is_correct=is_correct,
                    category=category or '',
                    subcategory=subcategory or '',
                    answered_at=datetime.utcnow()
                )
                db.add(user_answer_record)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error saving user answer: {e}")
            return False
        finally:
            db.close()

    def create_question_with_subcategory(self, category: str, sub_category: str, 
                                       question_text: str, options: List[str], 
                                       correct_answer: str, hint: str = None):
        """Create a new question with subcategory"""
        db = self.get_db()
        try:
            question = Question(
                category=category,
                sub_category=sub_category,
                question_text=question_text,
                options=json.dumps(options),
                correct_answer=correct_answer,
                hint=hint
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            return question.id
        finally:
            db.close()
    
    def clear_category_questions(self, category: str):
        """Clear all questions for a specific category"""
        db = self.get_db()
        try:
            deleted_count = db.query(Question).filter(Question.category == category).delete()
            db.commit()
            print(f"Deleted {deleted_count} questions for category '{category}'")
            return deleted_count
        finally:
            db.close()
    
    def add_question_with_image(self, category: str, sub_category: str, question_text: str, 
                               options: List[str], correct_answer: str, hint: str = None, 
                               image_path: str = None) -> int:
        """Add a new question with optional image to database"""
        db = self.get_db()
        try:
            question = Question(
                category=category,
                sub_category=sub_category,
                question_text=question_text,
                options=json.dumps(options),
                correct_answer=correct_answer,
                hint=hint,
                image_path=image_path,
                verified=False
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            return question.id
        finally:
            db.close()
    
    def update_question_image(self, question_id: int, image_path: str) -> bool:
        """Update image path for existing question"""
        db = self.get_db()
        try:
            question = db.query(Question).filter(Question.id == question_id).first()
            if question:
                question.image_path = image_path
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def get_all_modules(self):
        """Get all modules for admin management with subcategories"""
        db = self.get_db()
        try:
            from sqlalchemy import text
            
            # Get modules first
            modules_result = db.execute(text('''
                SELECT id, name, display_name, description, icon, color, is_premium, is_active, price
                FROM modules
                WHERE is_active = true OR is_active IS NULL
                ORDER BY is_premium ASC, name ASC
            ''')).fetchall()
            
            modules = []
            for row in modules_result:
                module_id = row[0]
                module_name = row[1]
                
                # Use module name directly (names now match between tables)
                question_category = module_name
                
                # Get total questions count for this category
                total_count_result = db.execute(text('''
                    SELECT COUNT(*) FROM questions WHERE category = :category
                '''), {'category': question_category}).fetchone()
                
                total_questions = total_count_result[0] if total_count_result else 0
                
                # Build topics/submodules list - create one topic for each module
                topics = []
                if total_questions > 0:
                    # Create a single topic representing all questions in this module
                    if module_name == 'Screening Test':
                        topic_name = 'Тест'
                        topic_description = 'Скрининговый тест для оценки базовых навыков'
                    elif module_name == 'Python':
                        topic_name = 'Основы Python'
                        topic_description = 'Вопросы по программированию на Python'
                    elif module_name == 'Machine Learning':
                        topic_name = 'Алгоритмы классификации'
                        topic_description = 'Машинное обучение и алгоритмы'
                    elif module_name == 'NLP':
                        topic_name = 'Обработка текста'
                        topic_description = 'Обработка естественного языка'
                    elif module_name == 'Computer Vision':
                        topic_name = 'Обработка изображений'
                        topic_description = 'Компьютерное зрение и обработка изображений'
                    else:
                        topic_name = 'Основы'
                        topic_description = f'Вопросы по {module_name}'
                    
                    topics.append({
                        'id': f"{module_name.lower().replace(' ', '_')}_{topic_name.lower().replace(' ', '_')}",
                        'name': topic_name,
                        'description': topic_description,
                        'icon': '📝',
                        'questions_count': total_questions,
                        'total_questions': total_questions
                    })
                
                # Build module data
                modules.append({
                    'id': module_id,
                    'key': module_name.lower().replace(' ', '_'),
                    'name': module_name.lower().replace(' ', '_'),
                    'display_name': row[2] or module_name,
                    'description': row[3] or f"Тестирование знаний по {module_name}",
                    'icon': row[4] or '📚',
                    'color': row[5] or '#FF6B35',
                    'is_premium': bool(row[6]),
                    'is_active': True,
                    'price': row[8] or 0,
                    'topics': topics,
                    'submodules': topics  # For compatibility
                })
            
            return modules
            
        except Exception as e:
            print(f"Error in get_all_modules: {e}")
            return []
        finally:
            db.close()
    
    def create_module(self, name: str, description: str, icon: str = '📚', 
                     is_premium: bool = False, price: float = 0.0) -> int:
        """Create new module"""
        db = self.get_db()
        try:
            from sqlalchemy import text
            
            result = db.execute(text('''
                INSERT INTO modules (name, display_name, description, icon, is_premium, price, is_active)
                VALUES (:name, :display_name, :description, :icon, :is_premium, :price, true)
                RETURNING id
            '''), {
                'name': name,
                'display_name': name,
                'description': description,
                'icon': icon,
                'is_premium': is_premium,
                'price': price
            })
            
            module_id = result.fetchone()[0]
            db.commit()
            return module_id
        except Exception as e:
            print(f"Error creating module: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def update_module_premium_status(self, module_id: int, is_premium: bool, price: float = 0.0):
        """Update module premium status and price"""
        db = self.get_db()
        try:
            # Using raw SQL for PostgreSQL
            from sqlalchemy import text
            
            result = db.execute(text('''
                UPDATE modules 
                SET is_premium = :is_premium, price = :price, updated_at = CURRENT_TIMESTAMP
                WHERE id = :module_id
            '''), {
                'is_premium': is_premium,
                'price': price,
                'module_id': module_id
            })
            
            db.commit()
            return result.rowcount > 0
        except Exception as e:
            print(f"Error updating module premium status: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def is_module_premium(self, module_name: str) -> tuple:
        """Check if module is premium and get price"""
        db = self.get_db()
        try:
            from sqlalchemy import text
            
            result = db.execute(text('''
                SELECT is_premium, price, display_name
                FROM modules
                WHERE name = :name
            '''), {'name': module_name}).fetchone()
            
            if result:
                return bool(result[0]), result[1], result[2]
            return False, 0.0, module_name
        except Exception as e:
            print(f"Error checking module premium status: {e}")
            return False, 0.0, module_name
        finally:
            db.close()

    def get_subcategories_for_module(self, module_name: str) -> list:
        """Get unique subcategories for a module"""
        db = self.get_db()
        try:
            # Get unique subcategories from questions table
            subcategories = db.query(Question.sub_category).filter(
                Question.category == module_name,
                Question.sub_category.isnot(None)
            ).distinct().all()
            
            result = []
            for sub in subcategories:
                if sub[0]:  # Check if subcategory is not None
                    result.append({
                        'name': sub[0],
                        'description': f"Вопросы по {sub[0]}",
                        'icon': '📝'
                    })
            
            return result
        except Exception as e:
            print(f"Error getting subcategories for {module_name}: {e}")
            return []
        finally:
            db.close()

    def count_questions_by_subcategory(self, module_name: str, subcategory: str) -> int:
        """Count questions in a specific subcategory"""
        db = self.get_db()
        try:
            count = db.query(Question).filter(
                Question.category == module_name,
                Question.sub_category == subcategory
            ).count()
            return count
        except Exception as e:
            print(f"Error counting questions for {module_name}/{subcategory}: {e}")
            return 0
        finally:
            db.close()

    def count_questions_by_category(self, category: str) -> int:
        """Count all questions in a category"""
        db = self.get_db()
        try:
            count = db.query(Question).filter(
                Question.category == category
            ).count()
            return count
        except Exception as e:
            print(f"Error counting questions for category {category}: {e}")
            return 0
        finally:
            db.close()
    
    def save_user_answer(self, user_id: str, question_id: int, category: str, 
                        selected_answer: str, is_correct: bool):
        """Save user's answer to database"""
        db = self.get_db()
        try:
            print(f"[DEBUG] Attempting to save answer: user_id={user_id}, question_id={question_id}, category={category}")
            
            answer = UserAnswer(
                user_id=user_id,
                question_id=question_id,
                category=category,
                selected_answer=selected_answer,
                is_correct=is_correct
            )
            db.add(answer)
            print(f"[DEBUG] Answer added to session, committing...")
            db.commit()
            print(f"[DEBUG] Answer committed successfully")
            
            # Update user progress
            self._update_user_progress(db, user_id, category)
            print(f"[DEBUG] User progress updated")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save answer: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def _update_user_progress(self, db, user_id: str, category: str):
        """Update user progress for a category"""
        # Get user's answers for this category
        answers = db.query(UserAnswer).filter(
            UserAnswer.user_id == user_id,
            UserAnswer.category == category
        ).all()
        
        # Count only unique questions answered
        unique_question_ids = set([a.question_id for a in answers])
        total_questions = len(unique_question_ids)
        
        # For each unique question, check if the latest answer is correct
        correct_answers = 0
        for question_id in unique_question_ids:
            latest_answer = db.query(UserAnswer).filter(
                UserAnswer.user_id == user_id,
                UserAnswer.question_id == question_id
            ).order_by(UserAnswer.answered_at.desc()).first()
            if latest_answer and latest_answer.is_correct:
                correct_answers += 1
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Determine level
        if score_percentage >= 80:
            level = "Senior"
        elif score_percentage >= 60:
            level = "Middle"
        else:
            level = "Junior"
        
        # Update or create progress record
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.category == category
        ).first()
        
        if progress:
            progress.total_questions = total_questions
            progress.correct_answers = correct_answers
            progress.score_percentage = score_percentage
            progress.level = level
            progress.last_updated = datetime.utcnow()
        else:
            progress = UserProgress(
                user_id=user_id,
                category=category,
                total_questions=total_questions,
                correct_answers=correct_answers,
                score_percentage=score_percentage,
                level=level
            )
            db.add(progress)
        
        db.commit()
    
    def get_user_progress(self, user_id: str) -> Dict:
        """Get user's overall progress"""
        db = self.get_db()
        try:
            progress_records = db.query(UserProgress).filter(
                UserProgress.user_id == user_id
            ).all()
            
            categories = []
            category_dict = {}
            total_questions = 0
            total_correct = 0
            
            for record in progress_records:
                category_data = {
                    'category': record.category,
                    'total': record.total_questions,
                    'correct': record.correct_answers,
                    'score': record.score_percentage,
                    'level': record.level,
                    'last_updated': record.last_updated.isoformat()
                }
                categories.append(category_data)
                category_dict[record.category] = category_data
                
                total_questions += record.total_questions
                total_correct += record.correct_answers
            
            overall_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            # Determine overall level
            if overall_score >= 80:
                overall_level = "Senior"
            elif overall_score >= 60:
                overall_level = "Middle"  
            else:
                overall_level = "Junior"
            
            return {
                'categories': categories,  # List format for frontend
                'category_dict': category_dict,  # Dict format for backward compatibility
                'total_answered': total_questions,
                'total_correct': total_correct,
                'overall_score': overall_score,
                'overall_level': overall_level,
                'overall': {
                    'score': overall_score,
                    'level': overall_level,
                    'total_answered': total_questions,
                    'total_correct': total_correct
                }
            }
        finally:
            db.close()
    
    def get_user_answers_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's recent answer history"""
        db = self.get_db()
        try:
            answers = db.query(UserAnswer).filter(
                UserAnswer.user_id == user_id
            ).order_by(UserAnswer.answered_at.desc()).limit(limit).all()
            
            return [{
                'category': answer.category,
                'is_correct': answer.is_correct,
                'answered_at': answer.answered_at.isoformat()
            } for answer in answers]
        finally:
            db.close()
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile information"""
        db = self.get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            return {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'telegram_username': user.telegram_username,
                'telegram_first_name': user.telegram_first_name,
                'telegram_last_name': user.telegram_last_name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_active': user.last_active.isoformat() if user.last_active else None
            }
        finally:
            db.close()
    
    def get_category_stats(self, user_id: str, category: str) -> Dict:
        """Get user's statistics for a specific category"""
        db = self.get_db()
        try:
            progress = db.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.category == category
            ).first()
            
            if progress:
                return {
                    'total': progress.total_questions,
                    'correct': progress.correct_answers,
                    'score': progress.score_percentage,
                    'level': progress.level,
                    'last_updated': progress.last_updated.isoformat()
                }
            else:
                return {
                    'total': 0,
                    'correct': 0,
                    'score': 0.0,
                    'level': 'Junior',
                    'last_updated': None
                }
        finally:
            db.close()
    
    def get_subcategory_stats(self, user_id: str, category: str, subcategory: str) -> Dict:
        """Get user's statistics for a specific subcategory"""
        db = self.get_db()
        try:
            # Special handling for Screening Test -> Тест
            if category == 'Screening Test' and subcategory == 'Тест':
                # Get all questions from Screening Test category (they all have sub_category = 'Тест')
                questions = db.query(Question).filter(
                    Question.category == 'Screening Test'
                ).all()
            else:
                # Get all questions for this subcategory
                questions = db.query(Question).filter(
                    Question.category == category,
                    Question.sub_category == subcategory
                ).all()
            
            if not questions:
                return {
                    'total': 0,
                    'correct': 0,
                    'score': 0.0,
                    'level': 'Junior'
                }
            
            # Get user's answers for these questions (only unique questions)
            question_ids = [q.id for q in questions]
            print(f"[DEBUG] Looking for answers for questions {question_ids} by user {user_id}")
            
            user_answers = db.query(UserAnswer).filter(
                UserAnswer.user_id == user_id,
                UserAnswer.question_id.in_(question_ids)
            ).all()
            
            print(f"[DEBUG] Found {len(user_answers)} answers for subcategory {subcategory}")
            
            # Count unique questions answered
            unique_questions_answered = len(set([a.question_id for a in user_answers]))
            
            # For each unique question, get the most recent answer to determine correctness
            correct_answers = 0
            for question_id in set([a.question_id for a in user_answers]):
                latest_answer = db.query(UserAnswer).filter(
                    UserAnswer.user_id == user_id,
                    UserAnswer.question_id == question_id
                ).order_by(UserAnswer.answered_at.desc()).first()
                if latest_answer and latest_answer.is_correct:
                    correct_answers += 1
            
            total_answered = unique_questions_answered
            
            if total_answered > 0:
                score = (correct_answers / total_answered) * 100
                if score >= 80:
                    level = 'Senior'
                elif score >= 60:
                    level = 'Middle'
                else:
                    level = 'Junior'
            else:
                score = 0.0
                level = 'Junior'
            
            return {
                'total': total_answered,
                'correct': correct_answers,
                'score': score,
                'level': level
            }
        finally:
            db.close()
    
    def get_recent_answers(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's recent answers for progress tracking"""
        db = self.get_db()
        try:
            answers = db.query(UserAnswer).filter(
                UserAnswer.user_id == user_id
            ).order_by(UserAnswer.answered_at.desc()).limit(limit).all()
            
            return [{
                'category': answer.category,
                'is_correct': answer.is_correct,
                'answered_at': answer.answered_at.isoformat(),
                'question_id': answer.question_id,
                'selected_answer': answer.selected_answer
            } for answer in answers]
        finally:
            db.close()

    # New methods for modules and submodules management
    def get_all_modules(self) -> List[Dict]:
        """Get all modules with their submodules"""
        db = self.get_db()
        try:
            modules = db.query(Module).order_by(Module.name).all()
            result = []
            for module in modules:
                submodules = db.query(Submodule).filter(Submodule.module_id == module.id).all()
                result.append({
                    'id': module.id,
                    'name': module.name,
                    'description': module.description,
                    'icon': module.icon,
                    'color': module.color,
                    'submodules': [{
                        'id': sub.id,
                        'name': sub.name,
                        'description': sub.description,
                        'icon': sub.icon,
                        'difficulty': sub.difficulty
                    } for sub in submodules]
                })
            return result
        finally:
            db.close()



    def create_submodule(self, module_id: int, name: str, description: str = None, 
                        icon: str = None, difficulty: str = None) -> Dict:
        """Create a new submodule"""
        db = self.get_db()
        try:
            submodule = Submodule(
                module_id=module_id,
                name=name,
                description=description,
                icon=icon,
                difficulty=difficulty
            )
            db.add(submodule)
            db.commit()
            db.refresh(submodule)
            return {
                'id': submodule.id,
                'module_id': submodule.module_id,
                'name': submodule.name,
                'description': submodule.description,
                'icon': submodule.icon,
                'difficulty': submodule.difficulty
            }
        finally:
            db.close()

    def get_questions_by_submodule(self, submodule_id: int) -> List[Dict]:
        """Get questions for a specific submodule"""
        db = self.get_db()
        try:
            questions = db.query(Question).filter(
                Question.submodule_id == submodule_id
            ).all()
            
            return [{
                'id': q.id,
                'question': q.question_text,
                'options': json.loads(q.options),
                'correct_answer': q.correct_answer,
                'hint': q.hint,
                'verified': q.verified
            } for q in questions]
        finally:
            db.close()

    def get_submodule_by_id(self, submodule_id: int) -> Dict:
        """Get submodule by ID"""
        db = self.get_db()
        try:
            submodule = db.query(Submodule).filter(Submodule.id == submodule_id).first()
            if not submodule:
                return {}
            
            # Get parent module info
            module = db.query(Module).filter(Module.id == submodule.module_id).first()
            
            return {
                'id': submodule.id,
                'name': submodule.name,
                'description': submodule.description,
                'icon': submodule.icon,
                'difficulty': submodule.difficulty,
                'module': {
                    'id': module.id,
                    'name': module.name
                } if module else None
            }
        finally:
            db.close()

    def get_module_by_id(self, module_id: int) -> Dict:
        """Get module by ID"""
        db = self.get_db()
        try:
            module = db.query(Module).filter(Module.id == module_id).first()
            if not module:
                return {}
            
            return {
                'id': module.id,
                'name': module.name,
                'description': module.description,
                'icon': module.icon,
                'color': module.color
            }
        finally:
            db.close()
    
    def save_first_test_result(self, user_id: str, category: str, subcategory: str, 
                              score: int, total_questions: int) -> bool:
        """Save user's first test result for social comparison"""
        db = self.get_db()
        try:
            # Check if user already has a first result for this test
            existing = db.query(FirstTestResult).filter(
                FirstTestResult.user_id == user_id,
                FirstTestResult.category == category,
                FirstTestResult.subcategory == subcategory
            ).first()
            
            if existing:
                # User already has a first result, don't save again
                return False
            
            # Calculate percentage
            score_percentage = (score / total_questions * 100) if total_questions > 0 else 0
            
            # Save first result
            first_result = FirstTestResult(
                user_id=user_id,
                category=category,
                subcategory=subcategory,
                score=score,
                total_questions=total_questions,
                score_percentage=score_percentage
            )
            db.add(first_result)
            db.commit()
            print(f"✓ Saved first test result for user {user_id}: {category} - {subcategory} = {score}/{total_questions}")
            return True
        except Exception as e:
            print(f"Error saving first test result: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_test_social_stats(self, category: str, subcategory: str, user_score: int) -> Dict:
        """Get social comparison statistics for a test"""
        db = self.get_db()
        try:
            # Get all first results for this test
            results = db.query(FirstTestResult).filter(
                FirstTestResult.category == category,
                FirstTestResult.subcategory == subcategory
            ).all()
            
            if not results:
                return {
                    'average_score': 0,
                    'average_percentage': 0,
                    'total_users': 0,
                    'better_than_percentage': 0,
                    'user_is_first': True
                }
            
            # Calculate statistics
            total_users = len(results)
            scores = [r.score for r in results]
            average_score = sum(scores) / len(scores) if scores else 0
            
            # Calculate average percentage
            percentages = [r.score_percentage for r in results]
            average_percentage = sum(percentages) / len(percentages) if percentages else 0
            
            # Calculate how many users scored lower than current user
            users_with_lower_score = len([s for s in scores if s < user_score])
            better_than_percentage = (users_with_lower_score / total_users * 100) if total_users > 0 else 0
            
            return {
                'average_score': round(average_score, 1),
                'average_percentage': round(average_percentage, 1),
                'total_users': total_users,
                'better_than_percentage': round(better_than_percentage),
                'user_is_first': False
            }
        except Exception as e:
            print(f"Error getting social stats: {e}")
            return {
                'average_score': 0,
                'average_percentage': 0,
                'total_users': 0,
                'better_than_percentage': 0,
                'user_is_first': True
            }
        finally:
            db.close()

# Initialize database manager
db_manager = DatabaseManager()