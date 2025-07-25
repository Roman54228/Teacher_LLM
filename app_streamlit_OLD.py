"""
Interview Prep - Main Streamlit Application
Beautiful gradient design with XP system and level progression
"""
import streamlit as st
from utils.db_progress_tracker import DatabaseProgressTracker

# Configure page
st.set_page_config(
    page_title="Interview Prep",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful design
st.markdown("""
<style>
    .main {
        padding: 0;
    }
    
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp {
        margin: 0;
        padding: 0;
    }
    
    /* Hide Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styles */
    .stButton > button {
        border-radius: 12px;
        border: none;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Radio button custom styling */
    .stRadio > div {
        flex-direction: column;
    }
    
    .stRadio > div > label {
        background: white;
        border: 2px solid #e5e5ea;
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        border-color: #007AFF;
        background: #f0f8ff;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #007AFF, #5AC8FA);
    }
</style>
""", unsafe_allow_html=True)


def load_questions():
    """Load questions from database or JSON file if database is empty"""
    progress_tracker = DatabaseProgressTracker()
    categories = progress_tracker.get_all_categories()
    
    if not categories:
        import json
        import os
        
        # Try to load from Russian questions file first
        ru_questions_file = 'data/questions_ru.json'
        en_questions_file = 'data/questions.json'
        
        questions_file = ru_questions_file if os.path.exists(ru_questions_file) else en_questions_file
        
        if os.path.exists(questions_file):
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            # Load questions to database
            from utils.database import db_manager
            db_manager.load_questions_to_db(questions_data)
            st.success("Вопросы загружены в базу данных!")
        else:
            st.error("Файл с вопросами не найден!")


def get_level_from_score(score):
    """Determine user level based on score percentage"""
    if score >= 85:
        return "Senior", "🏆", "#34C759"
    elif score >= 70:
        return "Middle", "🥈", "#FFD60A"
    elif score >= 40:
        return "Junior", "🥉", "#007AFF"
    else:
        return "Beginner", "📚", "#FF9500"


def display_question(question_data, question_index, category):
    """Display a single question with options"""
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 4px solid #007AFF;
    ">
        <h3 style="margin: 0 0 20px 0; color: #1d1d1f;">{question_data['question_text']}</h3>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Initialize database and load questions
    load_questions()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Initialize progress tracker
    progress_tracker = DatabaseProgressTracker()
    
    # Main application header with gradient design
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #007AFF 0%, #0056cc 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    ">
        <h1 style="margin: 0; font-size: 36px; font-weight: 700;">🧠 Interview Prep</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">
            Подготовка к техническим собеседованиям с ИИ
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user progress for overview
    total_answered = progress_tracker.get_total_questions_answered()
    overall_score = progress_tracker.get_overall_score()
    
    if total_answered > 0:
        level, emoji, color = get_level_from_score(overall_score)
        
        # Display user stats with beautiful cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                border-left: 4px solid {color};
            ">
                <div style="font-size: 40px; margin-bottom: 10px;">{emoji}</div>
                <div style="font-size: 18px; font-weight: 600; color: #1d1d1f;">Текущий уровень</div>
                <div style="font-size: 24px; font-weight: 700; color: {color}; margin-top: 5px;">{level}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                border-left: 4px solid #007AFF;
            ">
                <div style="font-size: 40px; margin-bottom: 10px;">📊</div>
                <div style="font-size: 18px; font-weight: 600; color: #1d1d1f;">Общий балл</div>
                <div style="font-size: 24px; font-weight: 700; color: #007AFF; margin-top: 5px;">{overall_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                border-left: 4px solid #34C759;
            ">
                <div style="font-size: 40px; margin-bottom: 10px;">✅</div>
                <div style="font-size: 18px; font-weight: 600; color: #1d1d1f;">Отвечено</div>
                <div style="font-size: 24px; font-weight: 700; color: #34C759; margin-top: 5px;">{total_answered}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Navigation buttons with beautiful design
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Тестирование навыков", type="primary", use_container_width=True):
            st.switch_page("pages/skill_assessment.py")
    
    with col2:
        if st.button("📈 Прогресс и аналитика", use_container_width=True):
            st.switch_page("pages/progress_dashboard.py")
    
    # Welcome message for new users
    if total_answered == 0:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #34C759 0%, #30D158 100%);
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            color: white;
            margin: 30px 0;
        ">
            <div style="font-size: 50px; margin-bottom: 15px;">🚀</div>
            <h2 style="margin: 0; font-size: 24px;">Добро пожаловать!</h2>
            <p style="margin: 10px 0; font-size: 16px; opacity: 0.9;">
                Начните с тестирования навыков, чтобы узнать свой уровень
            </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()