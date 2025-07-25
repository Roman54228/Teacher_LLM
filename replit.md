# Interview Prep - Telegram Mini App

## Overview

This is a Telegram Mini App for interview preparation featuring skill assessment tests with a hierarchical structure: Screening Test (always available), Python (free), and premium modules (ML, NLP, Computer Vision, Deep Learning). The app includes level evaluation (Junior/Middle/Senior), gamification elements, progress tracking, AI-powered explanations using YandexGPT API, and a modern mobile-first interface with Russian language support.

## User Preferences

- **Platform**: Telegram Mini App (not web application)
- **Language**: Russian interface and responses
- **Communication style**: Simple, everyday language
- **AI Service**: YandexGPT for explanations and recommendations
- **Admin Features**: Need admin panel for managing questions with correct answers and hints
- **AI Interaction**: Interactive chat with AI model for explanations, not just single responses
- **Deployment**: Local deployment only, no cloud platforms or web domains needed
- **Database**: SQLite preferred for simplicity over PostgreSQL
- **Configuration**: YAML configuration file instead of environment variables
- **Telegram Integration**: Simple bot setup without ngrok initially
- **Frontend**: Custom beautiful frontend with FastAPI backend (no Streamlit dependencies)
- **Design**: Modern gradient design with XP system, level progression, and mobile-first approach
- **Authentication**: Telegram authentication with personal user profiles for individual result tracking
- **Color Scheme**: Beige-orange gradient background (#F5E6D3, #E8C4A0, #D4A574, #C8956D) with orange accents (#FF6B35, #FF8C42)
- **Progress Indicators**: Green for fully completed subcategories (✅), Orange for partially completed with N/M format (⚠️), Default for not started
- **Navigation**: Modern bottom navigation with SVG icons (not emoji) and 5 sections: Home, Analytics, Tasks, Content, Knowledge Base

## System Architecture

### Frontend Architecture
- **Framework**: Custom HTML/CSS/JavaScript with FastAPI backend (no Streamlit)
- **Structure**: Single-page web application optimized for Telegram Mini App
- **User Interface**: Beautiful beige-orange gradient background with glass effects and backdrop-filter blur
- **Design System**: Modern navigation panel, bottom navigation with SVG icons, iOS-inspired cards
- **Interactive Elements**: Skills assessment cards, progress tracking, level indicators, knowledge base categories
- **Navigation**: 5-section bottom navigation: Home (🏠), Analytics (📊), Tasks (✅), Content (📈), Knowledge Base (📚)
- **Integration**: Telegram Bot API for user interaction and Web App launching

### Backend Architecture
- **Language**: Python
- **Framework**: FastAPI with automatic API documentation and type safety
- **Architecture Pattern**: Modern async-first structure with Pydantic models
- **Data Storage**: PostgreSQL/SQLite database for persistent storage of questions and user progress
- **Session Management**: Database-backed user sessions with persistent progress tracking
- **Database ORM**: SQLAlchemy for database operations and models
- **Server**: Uvicorn ASGI server for high-performance async request handling

### AI Integration
- **Service**: YandexGPT for intelligent explanations and recommendations
- **Usage**: Question explanations, personalized learning recommendations
- **API Management**: Environment variable-based API key configuration (YANDEX_API_KEY, YANDEX_FOLDER_ID)

## Key Components

### 1. Modular Learning System with Screening Test
- **Data Structure**: `data/modules.json` + special Screening Test module
- **Purpose**: Organized learning structure with modules containing topics
- **Special Module**: Screening Test (🎯) - always accessible, first in list, 10 mixed questions
- **Regular Modules**: Machine Learning, Python, NLP, Computer Vision
- **Topics per Module**: Each module contains 3-4 specialized topics (e.g., ML: Linear Models, Trees, Unsupervised Learning)
- **Features**: Progress tracking per topic, difficulty levels, question counts
- **UI**: Module cards with statistics, topic navigation with back buttons, modern gradient design
- **Screening Integration**: Special handling for screening test routing and progress tracking

### 1a. Analytics Integration - Yandex Metrica
- **Counter ID**: 103395184 (real counter - active and configured)
- **Purpose**: Comprehensive user behavior analytics and app usage tracking
- **Event Tracking**: Test starts/completions, AI interactions, navigation, question answers
- **Page Views**: Automatic tracking of all app sections and test categories
- **Features**: Click maps, webvisor, bounce rate tracking, hash navigation support
- **Telegram Integration**: User ID tracking, mini app optimized settings
- **Key Events**: `test_start`, `test_complete`, `ai_chat_start`, `navigation`, `question_answered`
- **Setup Guide**: See `YANDEX_METRICA_GUIDE.md` for complete configuration instructions

### 1a. Question Management System
- **Database Table**: `questions`
- **Purpose**: Centralized storage of assessment questions by category and topic
- **Structure**: PostgreSQL/SQLite table with ID, category, question text, options (JSON), correct answers, hints, and verification status
- **Categories**: Python, Machine Learning, NLP, Computer Vision, Screening Test
- **Admin Features**: FastAPI-powered admin panel for question management, hint assignment, and verification
- **Migration**: Questions initially loaded from `data/questions.json` into database

### 1a. User Authentication System
- **Database Tables**: `users` with Telegram ID fields
- **Purpose**: Telegram-based user authentication and personal profiles
- **Structure**: User table with session_id, telegram_id, telegram_username, telegram_first_name, telegram_last_name
- **Features**: Individual user profiles, personal progress tracking, Telegram data integration
- **API Endpoints**: /api/init (with Telegram user data), /api/profile (user profile information)

### 2. Progress Tracking System
- **File**: `utils/db_progress_tracker.py`
- **Class**: `DatabaseProgressTracker`
- **Database Tables**: `users`, `user_answers`, `user_progress`
- **Functionality**: 
  - Persistent user session management
  - Tracks answers by category with database storage
  - Maintains comprehensive user statistics
  - Records detailed answer history with timestamps
  - Calculates performance metrics and levels

### 3. AI Helper Module
- **File**: `utils/yandex_gpt_helper.py`
- **Purpose**: Interface with YandexGPT API for educational content
- **Features**:
  - Interactive chat sessions for question explanations
  - Personalized recommendations based on performance
  - Educational context and background knowledge
  - Session-based conversation history for follow-up questions

### 4. Assessment Interface
- **File**: `pages/skill_assessment.py`
- **Features**:
  - Category selection with descriptions
  - Interactive quiz interface
  - Previous performance display
  - Real-time progress tracking

### 5. Progress Dashboard
- **File**: `pages/progress_dashboard.py`
- **Components**:
  - Overview metrics and KPIs
  - Performance charts and visualizations
  - Detailed analysis by category
  - AI-powered recommendations

## Data Flow

1. **Quiz Selection**: User selects assessment category
2. **Question Delivery**: Questions loaded from JSON data store
3. **Answer Processing**: User responses tracked via ProgressTracker
4. **Performance Analysis**: Statistics calculated and stored in session state
5. **AI Enhancement**: YandexGPT API provides explanations and recommendations
6. **Dashboard Updates**: Progress visualizations updated in real-time

## External Dependencies

### Core Framework
- **FastAPI**: Modern, high-performance web framework with automatic API documentation
- **Custom Frontend**: Pure HTML/CSS/JavaScript without external frameworks
- **SQLAlchemy**: Database ORM for data management
- **Pydantic**: Data validation and serialization with type hints
- **Uvicorn**: Lightning-fast ASGI server for production deployment

### AI Services
- **YandexGPT API**: YandexGPT-lite model for explanations and recommendations
- **Authentication**: Environment variable-based API key management (YANDEX_API_KEY, YANDEX_FOLDER_ID)

### Data Visualization
- **Plotly Express**: Quick statistical charts
- **Plotly Graph Objects**: Custom interactive visualizations

## Deployment Strategy

### Environment Setup
- **Python Environment**: Standard Python 3.x with pip dependencies
- **Environment Variables**: YANDEX_API_KEY and YANDEX_FOLDER_ID for AI functionality
- **Data Files**: JSON-based question database in `data/` directory

### Session Management
- **Storage**: Database-backed user sessions with persistent progress tracking
- **Persistence**: PostgreSQL/SQLite database for permanent data storage
- **Scalability**: Multi-user deployment ready with concurrent access support

### Configuration
- **API Keys**: Environment variable configuration for YandexGPT
- **Data Sources**: Local JSON files for question content
- **Extensibility**: Modular structure allows easy addition of new categories

## Architecture Decisions

### JSON-Based Question Storage
- **Problem**: Need simple, readable question database
- **Solution**: JSON file storage with category-based organization
- **Rationale**: Easy to maintain, version control friendly, no database overhead
- **Trade-offs**: Limited concurrent access, manual data management

### Database-Based Progress Tracking
- **Problem**: Need persistent user progress across sessions
- **Solution**: SQLite database with automatic fallback from PostgreSQL
- **Rationale**: Persistent storage, simple setup, no external dependencies
- **Trade-offs**: Single-file database, limited concurrent access for multi-user deployment

### YandexGPT Integration for Educational Content
- **Problem**: Provide detailed explanations and personalized recommendations
- **Solution**: YandexGPT API integration for dynamic content generation
- **Rationale**: High-quality explanations, personalized learning experience, Russian language support
- **Trade-offs**: API costs, external dependency, requires API key and folder ID

### Modular Page Architecture
- **Problem**: Organize complex multi-page application
- **Solution**: Separate page modules with utility functions
- **Rationale**: Clean code organization, reusable components
- **Trade-offs**: Multiple files to maintain, import dependencies

### 6. Social Comparison System
- **Database Table**: `first_test_results`
- **Purpose**: Track first-time test results for social comparison and community engagement
- **Structure**: PostgreSQL table storing user_id, category, subcategory, score, total_questions, score_percentage, and completion timestamp
- **Features**: 
  - Only saves first attempt results to prevent gaming the system
  - Calculates social statistics: average scores, user percentile ranking
  - Beautiful modal showing user performance vs community average
  - Real-time social feedback: "You performed better than X% of users"
- **API Endpoints**: `/api/test/complete` for social statistics retrieval
- **Integration**: Automatic display after test completion with animated modal

## Recent Changes
- **2025-07-25**: CONFIRMED FASTAPI ARCHITECTURE + LEGACY CLEANUP
  - **ПОДТВЕРЖДЕН FASTAPI**: Приложение полностью работает на FastAPI (main.py), НЕ на Flask
  - **АРХИТЕКТУРА**: main.py (порт 5002) + admin_fastapi.py (порт 5003)
  - **ВОЗМОЖНОСТИ**: Автодокументация /docs, Pydantic модели, async поддержка
  - **УБРАНА ПОДСВЕТКА**: Правильные ответы больше не подсвечиваются зеленым при неправильном выборе
  - **LEGACY CLEANUP**: Переименованы устаревшие Flask/Streamlit файлы в *_OLD.py для ясности
  - **АКТИВНЫЕ ФАЙЛЫ**: Только main.py и admin_fastapi.py используются в production
- **2025-07-24**: FASTAPI MIGRATION COMPLETED
  - **ПЕРЕПИСАНО на FastAPI**: Полная миграция с Flask на FastAPI для лучшей производительности
  - **СОЗДАНО main.py**: FastAPI основное приложение на порту 5002 с автодокументацией
  - **СОЗДАНО admin_fastapi.py**: FastAPI админ-панель на порту 5003
  - **ТЕСТИРОВАНО API**: Health check, user init, questions API работают корректно
  - **СОВРЕМЕННАЯ АРХИТЕКТУРА**: Pydantic модели, автоматическая документация, type hints
  - **СОВМЕСТИМОСТЬ**: Все существующие API endpoints сохранены и работают
  - **ПРОИЗВОДИТЕЛЬНОСТЬ**: Улучшенная скорость отклика и async поддержка
- **2025-07-24**: PREMIUM MODULE SYSTEM FULLY IMPLEMENTED
  - **FIXED database error**: Added missing columns (icon, color, created_at, updated_at) to modules table
  - **FIXED 500 errors**: Added db_path attribute to DatabaseManager class for SQLite operations
  - **COMPLETED premium UI**: Beautiful modal windows with purchase interface and notifications
  - **TESTED admin panel**: Module management now works without database errors
  - **VERIFIED purchase flow**: Premium module purchase system functional in test mode
  - **READY FOR TESTING**: Full premium module system ready for user testing and feedback
- **2025-07-24**: FINAL CODE UPDATE - ALL SYSTEMS OPTIMIZED AND PRODUCTION READY
  - **FIXED statistics display**: API now returns accurate user progress data instead of N/A values
  - **OPTIMIZED database queries**: Removed debug logging and cleaned up production code
  - **VERIFIED functionality**: Statistics show real results (answered questions, percentage scores, levels)
  - **ENHANCED user experience**: Proper answer feedback with green/red highlighting
  - **PRODUCTION READY**: Clean code without debug messages, ready for deployment
- **2025-07-23**: CRITICAL BUG FIXES - ALL SYSTEMS RESTORED AND FUNCTIONAL
  - **FIXED SyntaxError**: All JavaScript fetch() calls now use protocol-aware URLs (HTTP/HTTPS auto-detection)
  - **FIXED 500 errors**: Added missing `get_question_by_id()` method to DatabaseManager class
  - **FIXED module display**: Added `questions_count` field - now shows "15 вопросов" instead of "0 вопросов"
  - **FIXED API routing**: Added `/api/subcategory/<category>/<subcategory>/questions` with category mapping
  - **TESTED and VERIFIED**: All API endpoints return correct data, no more HTML-instead-of-JSON issues
  - **DATABASE STATUS**: 15 Screening Test + 15 Python questions properly categorized and accessible
  - **DEPLOYMENT READY**: Files ready for production deployment on filonov.space domain
- **2025-07-23**: Created comprehensive production deployment solution
  - Generated complete Docker deployment setup with interactive access (Dockerfile, docker-compose.yml, docker-setup.sh)
  - Created automated deployment script (deploy.sh) supporting both localhost and remote server deployment
  - Built production-optimized app version (production_app.py) with logging, security, error handling
  - Developed multiple deployment guides: PRODUCTION_DEPLOYMENT_GUIDE.md, QUICK_DEPLOYMENT.md, SIMPLE_SOLUTION.md, DOCKER_DEPLOYMENT.md
  - Added production requirements file with optimized dependencies
  - User preference: prioritize simple deployment over Docker complexity
- **2025-07-22**: Added comprehensive social comparison system
  - Created `FirstTestResult` database table for tracking first-time test results
  - Implemented social statistics calculation (average scores, percentile rankings)
  - Added beautiful modal showing user performance vs community
  - Created `/api/test/complete` endpoint for social data
  - Users now see "You performed better than X% of people" after tests
  - System prevents gaming by only tracking first attempts per test
- **2025-07-20**: Successfully unified Screening Test module implementation
  - Removed all special logic and hardcoded values for Screening Test
  - Created proper database structure: "Screening Test" → "Тест" → 15 unique questions
  - Unified progress tracking system - now works identically to Python module
  - Fixed module ordering: free modules (Screening Test, Python) first, premium modules last
- Successfully added 15 comprehensive Python questions in Russian across 11 subcategories (Основы Python, ООП, Структуры данных, etc.)
- Updated database with 40 total questions, all with hint system implemented
- Python module now fully functional with proper subcategory navigation and progress tracking