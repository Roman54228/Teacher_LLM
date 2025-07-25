"""
FastAPI Admin Panel for Interview Prep App
Переписанная админ-панель с Flask на FastAPI
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Depends, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import secrets

# Local imports
from config_loader import config
from utils.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
logger.info("✓ Конфигурация загружена из config.yaml")

# Initialize database
db_manager = DatabaseManager()
logger.info("✓ База данных инициализирована для админ-панели")

# Initialize FastAPI app
app = FastAPI(
    title="Interview Prep - Admin Panel",
    description="Administrative interface for managing questions and modules",
    version="2.0.0"
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

# Basic authentication
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Simple admin authentication"""
    admin_config = config.get('admin', {})
    correct_username = admin_config.get('username', 'admin')
    correct_password = admin_config.get('password', 'admin123')
    
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Pydantic models
class ModuleCreate(BaseModel):
    name: str
    description: str
    icon: str = "📚"
    is_premium: bool = False
    price: float = 0.0

class QuestionCreate(BaseModel):
    category: str
    sub_category: str
    question_text: str
    options: List[str]
    correct_answers: List[str]
    hint: Optional[str] = None
    image_path: Optional[str] = None

class ModulePremiumUpdate(BaseModel):
    is_premium: bool
    price: Optional[float] = 0.0

# Routes
@app.get("/", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, username: str = Depends(get_current_user)):
    """Admin dashboard"""
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "username": username
    })

@app.get("/admin/modules", response_class=HTMLResponse)
async def admin_modules(request: Request, username: str = Depends(get_current_user)):
    """Module management page"""
    return templates.TemplateResponse("admin_modules.html", {
        "request": request,
        "username": username
    })

@app.get("/admin/questions", response_class=HTMLResponse)
async def admin_questions(request: Request, username: str = Depends(get_current_user)):
    """Question management page"""
    return templates.TemplateResponse("admin_questions.html", {
        "request": request,
        "username": username
    })

@app.get("/admin/add_question", response_class=HTMLResponse)
async def add_question_form(request: Request, username: str = Depends(get_current_user)):
    """Add question form"""
    categories = db_manager.get_all_modules()
    return templates.TemplateResponse("admin_add_question.html", {
        "request": request,
        "username": username,
        "categories": categories
    })

@app.get("/admin/add_image_question", response_class=HTMLResponse)
async def add_image_question_form(request: Request, username: str = Depends(get_current_user)):
    """Add image question form"""
    categories = db_manager.get_all_modules()
    return templates.TemplateResponse("admin_add_image_question.html", {
        "request": request,
        "username": username,
        "categories": categories
    })

# API endpoints
@app.get("/admin/api/stats")
async def get_admin_stats(username: str = Depends(get_current_user)):
    """Get admin dashboard statistics"""
    try:
        stats = {
            'total_questions': db_manager.get_total_questions(),
            'total_users': db_manager.get_total_users(),
            'total_modules': len(db_manager.get_all_modules()),
            'recent_activity': db_manager.get_recent_activity(),
            'categories_stats': db_manager.get_categories_stats()
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to load statistics")

@app.get("/api/modules")
async def get_modules():
    """Get all modules"""
    try:
        modules = db_manager.get_all_modules()
        return modules
    except Exception as e:
        logger.error(f"Error getting modules: {e}")
        raise HTTPException(status_code=500, detail="Failed to load modules")

@app.post("/api/modules")
async def create_module(module: ModuleCreate, username: str = Depends(get_current_user)):
    """Create new module"""
    try:
        module_id = db_manager.create_module(
            name=module.name,
            description=module.description,
            icon=module.icon,
            is_premium=module.is_premium,
            price=module.price
        )
        
        if module_id:
            return {"success": True, "message": "Модуль создан успешно", "module_id": module_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create module")
            
    except Exception as e:
        logger.error(f"Error creating module: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modules/{module_id}/premium")
async def update_module_premium(module_id: int, update_data: ModulePremiumUpdate, username: str = Depends(get_current_user)):
    """Update module premium status"""
    try:
        success = db_manager.update_module_premium_status(
            module_id, 
            update_data.is_premium, 
            update_data.price
        )
        
        if success:
            return {"success": True, "message": "Статус модуля обновлен"}
        else:
            raise HTTPException(status_code=404, detail="Module not found")
            
    except Exception as e:
        logger.error(f"Error updating module premium status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update module")

@app.delete("/api/modules/{module_id}")
async def delete_module(module_id: int, username: str = Depends(get_current_user)):
    """Delete module"""
    try:
        success = db_manager.delete_module(module_id)
        
        if success:
            return {"success": True, "message": "Модуль удален"}
        else:
            raise HTTPException(status_code=404, detail="Module not found")
            
    except Exception as e:
        logger.error(f"Error deleting module: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete module")

@app.get("/api/questions")
async def get_questions(category: Optional[str] = None, username: str = Depends(get_current_user)):
    """Get questions, optionally filtered by category"""
    try:
        if category:
            questions = db_manager.get_questions_by_category(category)
        else:
            questions = db_manager.get_all_questions()
        
        return questions
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to load questions")

@app.post("/api/questions")
async def create_question(question: QuestionCreate, username: str = Depends(get_current_user)):
    """Create new question"""
    try:
        question_id = db_manager.add_question(
            category=question.category,
            sub_category=question.sub_category,
            question_text=question.question_text,
            options=question.options,
            correct_answers=question.correct_answers,
            hint=question.hint,
            image_path=question.image_path
        )
        
        if question_id:
            return {"success": True, "message": "Вопрос добавлен успешно", "question_id": question_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create question")
            
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/questions/image")
async def create_image_question(
    category: str = Form(...),
    sub_category: str = Form(...),
    question_text: str = Form(...),
    options: str = Form(...),  # JSON string
    correct_answers: str = Form(...),  # JSON string
    hint: str = Form(""),
    image: UploadFile = File(...),
    username: str = Depends(get_current_user)
):
    """Create question with image"""
    try:
        # Parse JSON fields
        options_list = json.loads(options)
        correct_answers_list = json.loads(correct_answers)
        
        # Save uploaded image
        upload_dir = Path("static/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(image.filename).suffix
        image_filename = f"question_{timestamp}{file_extension}"
        image_path = upload_dir / image_filename
        
        # Save file
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Create question with image
        question_id = db_manager.add_question(
            category=category,
            sub_category=sub_category,
            question_text=question_text,
            options=options_list,
            correct_answers=correct_answers_list,
            hint=hint if hint else None,
            image_path=f"/static/uploads/{image_filename}"
        )
        
        if question_id:
            return {"success": True, "message": "Вопрос с изображением добавлен", "question_id": question_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create question")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in options or correct_answers")
    except Exception as e:
        logger.error(f"Error creating image question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: int, username: str = Depends(get_current_user)):
    """Delete question"""
    try:
        success = db_manager.delete_question(question_id)
        
        if success:
            return {"success": True, "message": "Вопрос удален"}
        else:
            raise HTTPException(status_code=404, detail="Question not found")
            
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete question")

@app.get("/api/subcategories/{category}")
async def get_subcategories(category: str, username: str = Depends(get_current_user)):
    """Get subcategories for category"""
    try:
        subcategories = db_manager.get_subcategories_by_module(category)
        return subcategories
    except Exception as e:
        logger.error(f"Error getting subcategories: {e}")
        raise HTTPException(status_code=500, detail="Failed to load subcategories")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "admin-panel",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": "connected" if db_manager else "disconnected"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI Admin Panel...")
    logger.info("✅ Admin Panel starting on 0.0.0.0:5001")
    
    uvicorn.run(
        "admin_fastapi:app",
        host="0.0.0.0",
        port=5003,
        reload=True,
        log_level="info"
    )