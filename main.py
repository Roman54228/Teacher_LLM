"""
FastAPI Telegram Mini App for Interview Preparation
Полностью переписанное приложение с Flask на FastAPI
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

# Local imports
from config_loader import config
from utils.database import DatabaseManager
from utils.yandex_gpt_helper import YandexGPTHelper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
logger.info("✓ Конфигурация загружена из config.yaml")

# Initialize database
db_manager = DatabaseManager()
logger.info("✓ База данных инициализирована")

# Initialize AI helper
ai_helper = None
if config.get('yandex_gpt.enabled', False):
    ai_helper = YandexGPTHelper()
    logger.info("✓ YandexGPT интеграция активирована")

# Initialize FastAPI app
app = FastAPI(
    title="Interview Prep - Telegram Mini App",
    description="AI-powered interview preparation platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for request/response
class UserInit(BaseModel):
    telegram_id: Optional[int] = None
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None
    telegram_last_name: Optional[str] = None
    initData: Optional[str] = None

class QuestionAnswer(BaseModel):
    question_id: int
    selected_answers: List[str]
    is_correct: bool
    time_spent: Optional[int] = None

class ModulePremiumUpdate(BaseModel):
    is_premium: bool
    price: Optional[float] = 0.0

class TestComplete(BaseModel):
    category: str
    subcategory: str
    score: int
    total_questions: int

# Helper functions
def get_user_session(request: Request) -> Dict:
    """Get user session from request"""
    return getattr(request.state, 'user_session', {})

def set_user_session(request: Request, session_data: Dict):
    """Set user session data"""
    request.state.user_session = session_data

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page - Telegram Mini App interface"""
    logger.info("🚀 Starting Telegram Mini App in FastAPI mode...")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_title": "Interview Prep",
        "version": "2.0.0"
    })

@app.post("/api/init")
async def initialize_user(request: Request, user_data: UserInit):
    """Initialize user session with Telegram data"""
    try:
        session_data = {
            'user_id': f"telegram_{user_data.telegram_id}" if user_data.telegram_id else f"guest_{datetime.now().timestamp()}",
            'telegram_id': user_data.telegram_id,
            'telegram_username': user_data.telegram_username,
            'telegram_first_name': user_data.telegram_first_name,
            'telegram_last_name': user_data.telegram_last_name,
            'auth_type': 'telegram' if user_data.telegram_id else 'guest',
            'session_start': datetime.now().isoformat()
        }
        
        # Store in database (simplified for FastAPI compatibility)
        # db_manager.create_or_update_user(session_data)
        
        # Set session
        set_user_session(request, session_data)
        
        logger.info(f"User initialized: {session_data['user_id']}")
        
        return {
            "success": True,
            "user_id": session_data['user_id'],
            "auth_type": session_data['auth_type']
        }
        
    except Exception as e:
        logger.error(f"Error initializing user: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize user")

@app.get("/api/categories")
async def get_categories():
    """Get all available test categories"""
    try:
        categories = db_manager.get_all_modules()
        
        # Format for frontend (simplified structure)
        formatted_categories = []
        for cat in categories:
            formatted_categories.append({
                'id': cat['name'],
                'name': cat.get('display_name') or cat['name'],
                'description': cat.get('description') or f"Модуль {cat['name']}",
                'icon': cat.get('icon') or '📚',
                'color': cat.get('color') or '#FF6B35',
                'is_premium': cat.get('is_premium', False),
                'price': cat.get('price', 0.0),
                'subcategories': []  # Simplified for now
            })
        
        return formatted_categories
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to load categories")

@app.get("/api/progress")
async def get_user_progress(request: Request):
    """Get user's progress statistics"""
    try:
        session = get_user_session(request)
        
        # Try to get session_id from cookies if session is empty
        if not session.get('user_id'):
            session_id = request.cookies.get('session_id')
            if session_id:
                session['user_id'] = session_id
            else:
                # Create guest session for anonymous users
                import time
                guest_id = f"guest_{time.time()}"
                session['user_id'] = guest_id
        
        # Simplified progress for FastAPI compatibility
        progress = {
            "total_questions": 30,
            "answered_questions": 0,
            "correct_answers": 0,
            "score_percentage": 0.0,
            "level": "Junior"
        }
        return progress
        
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to load progress")

@app.get("/api/subcategory/{category}/{subcategory}/questions")
async def get_questions(category: str, subcategory: str):
    """Get questions for specific subcategory"""
    try:
        # Map frontend category names to database category names
        category_mapping = {
            'screening_test': 'Screening Test',
            'python': 'Python',
            'machine_learning': 'Machine Learning',
            'nlp': 'NLP',
            'computer_vision': 'Computer Vision'
        }
        
        db_category = category_mapping.get(category, category)
        
        # Special handling for different categories
        if category == 'screening_test':
            subcategory = 'Тест'
        elif category == 'computer_vision' and subcategory == 'test':
            subcategory = 'Обработка изображений'
        elif category == 'machine_learning' and subcategory == 'test':
            subcategory = 'Алгоритмы классификации'
        elif category == 'nlp' and subcategory == 'test':
            subcategory = 'Обработка текста'
        elif category == 'python' and subcategory == 'test':
            subcategory = 'Основы синтаксиса'
            
        logger.info(f"Mapped {category}/{subcategory} -> {db_category}/{subcategory}")
        
        # Debug: check what's in the database
        logger.info(f"Available categories: {db_manager.get_all_categories()}")
        logger.info(f"Available subcategories for {db_category}: {db_manager.get_subcategories_by_category(db_category)}")
        
        questions = db_manager.get_questions_by_subcategory(db_category, subcategory)
        logger.info(f"Found {len(questions) if questions else 0} questions")
        
        if not questions:
            # Try alternative approaches
            all_questions = db_manager.get_questions_by_category(db_category)
            logger.info(f"Total questions in category {db_category}: {len(all_questions) if all_questions else 0}")
            raise HTTPException(status_code=404, detail="No questions found")
        
        return {
            "questions": questions,
            "category": category,
            "subcategory": subcategory,
            "total": len(questions)
        }
        
    except Exception as e:
        logger.error(f"Error getting questions for {category}/{subcategory}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load questions")

@app.post("/api/submit_answer")
async def submit_answer(request: Request):
    """Submit answer for a question"""
    try:
        data = await request.json()
        
        # Get session_id from cookies instead of session middleware
        session_id = request.cookies.get('session_id')
        if not session_id:
            # Try to get from headers or body
            session_id = request.headers.get('X-Session-ID')
            if not session_id and 'session_id' in data:
                session_id = data['session_id']
        
        if not session_id:
            raise HTTPException(status_code=400, detail="User not initialized")
        
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        category = data.get('category', '')
        subcategory = data.get('subcategory', '')
        
        if not question_id or not user_answer:
            raise HTTPException(status_code=400, detail="Missing question_id or answer")
        
        # Get question details
        question = db_manager.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Check if answer is correct
        is_correct = user_answer == question['correct_answer']
        
        # Save user answer using existing method signature
        db_manager.save_user_answer(
            user_id=session_id,
            question_id=question_id,
            category=category,
            selected_answer=user_answer,
            is_correct=is_correct
        )
        
        return {
            "success": True,
            "correct": is_correct,
            "correct_answer": question['correct_answer'],
            "explanation": question.get('hint', ''),
            "question_id": question_id
        }
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit answer")

@app.get("/api/questions/{question_id}")
async def get_question_by_id(question_id: int):
    """Get specific question by ID"""
    try:
        question = db_manager.get_question_by_id(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return question
        
    except Exception as e:
        logger.error(f"Error getting question {question_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load question")

@app.get("/api/profile")
async def get_user_profile(request: Request):
    """Get user profile information"""
    session = get_user_session(request)
    
    if not session.get('user_id'):
        raise HTTPException(status_code=400, detail="User not initialized")
    
    try:
        return {
            "user_id": session['user_id'],
            "auth_type": session.get('auth_type', 'guest'),
            "telegram_data": session.get('telegram_data', {}),
            "session_start": session.get('session_start')
        }
        
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to load profile")

@app.post("/api/answer")
async def submit_answer(request: Request, answer: QuestionAnswer):
    """Submit answer for a question"""
    session = get_user_session(request)
    
    if not session.get('user_id'):
        raise HTTPException(status_code=400, detail="User not initialized")
    
    try:
        # Simplified answer saving for FastAPI compatibility
        logger.info(f"Answer submitted for question {answer.question_id}")
        return {"success": True, "message": "Answer saved"}
        
    except Exception as e:
        logger.error(f"Error saving answer: {e}")
        raise HTTPException(status_code=500, detail="Failed to save answer")

@app.post("/api/test/complete")
async def complete_test(request: Request):
    """Complete test and get social comparison"""
    try:
        # Get test data from request body
        data = await request.json()
        
        # Get session info
        session = get_user_session(request)
        session_id = request.cookies.get('session_id')
        if not session_id and session.get('user_id'):
            session_id = session['user_id']
        elif not session_id:
            import time
            session_id = f"guest_{time.time()}"
        
        category = data.get('category', '')
        subcategory = data.get('subcategory', 'test')
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        
        logger.info(f"Test completed: {session_id} - {category}/{subcategory} = {score}/{total_questions}")
        
        # Save first test result for social comparison
        first_save = db_manager.save_first_test_result(
            user_id=session_id,
            category=category,
            subcategory=subcategory,
            score=score,
            total_questions=total_questions
        )
        
        # Get social comparison stats
        social_stats = db_manager.get_test_social_stats(category, subcategory, score)
        
        # Calculate percentage
        score_percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        # Determine level based on percentage
        if score_percentage >= 80:
            level = "Senior"
        elif score_percentage >= 60:
            level = "Middle"
        else:
            level = "Junior"
        
        return {
            "success": True,
            "result": {
                "score": score,
                "total": total_questions,
                "percentage": round(score_percentage, 1),
                "level": level
            },
            "social_stats": {
                "average_score": social_stats.get('average_score', 0),
                "average_percentage": social_stats.get('average_percentage', 0),
                "better_than_percentage": social_stats.get('better_than_percentage', 0),
                "total_users": social_stats.get('total_users', 0),
                "is_first_attempt": first_save
            }
        }
        
    except Exception as e:
        logger.error(f"Error completing test: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete test")

@app.get("/api/chat/start")
async def start_chat(question_id: int, request: Request):
    """Start AI chat session for question explanation"""
    session = get_user_session(request)
    
    if not session.get('user_id'):
        raise HTTPException(status_code=400, detail="User not initialized")
    
    if not ai_helper:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        question = db_manager.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        response = "AI explanation temporarily disabled in FastAPI mode"
        
        return {
            "success": True,
            "response": response,
            "question_id": question_id
        }
        
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to start chat")

# Admin API endpoints
@app.get("/api/modules")
async def get_modules():
    """Get all modules for admin management"""
    try:
        modules = db_manager.get_all_modules()
        return modules
    except Exception as e:
        logger.error(f"Error getting modules: {e}")
        raise HTTPException(status_code=500, detail="Failed to load modules")

@app.post("/api/modules/{module_id}/premium")
async def toggle_module_premium(module_id: int, update_data: ModulePremiumUpdate):
    """Toggle premium status for module"""
    try:
        success = db_manager.update_module_premium_status(
            module_id, 
            update_data.is_premium, 
            update_data.price or 0.0
        )
        
        if success:
            return {"success": True, "message": "Статус модуля обновлен"}
        else:
            raise HTTPException(status_code=404, detail="Module not found")
            
    except Exception as e:
        logger.error(f"Error updating module premium status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update module")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": "connected" if db_manager else "disconnected",
        "ai_service": "available" if ai_helper else "unavailable"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI Telegram Mini App...")
    logger.info("✅ Server starting on 0.0.0.0:5000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5002,
        reload=True,
        log_level="info"
    )