"""
Skill Assessment Page for Interview Prep
Enhanced with beautiful gradient design and XP system
"""
import json
import streamlit as st
from utils.db_progress_tracker import DatabaseProgressTracker
from utils.yandex_gpt_helper import get_ai_explanation


def show_skill_assessment():
    """
    Display the skill assessment page
    """
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #007AFF 0%, #0056cc 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    ">
        <h1 style="margin: 0; font-size: 32px; font-weight: 700;">📊 Skills Assessment</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Выберите направление для тестирования</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize progress tracker
    progress_tracker = DatabaseProgressTracker()
    
    # Load available categories
    categories = progress_tracker.get_all_categories()
    
    if not categories:
        st.error("Нет доступных категорий для тестирования")
        return
    
    # Display categories with beautiful cards
    cols = st.columns(2)
    
    category_info = {
        'Python': {'icon': '🐍', 'color': '#007AFF'},
        'Machine Learning': {'icon': '🤖', 'color': '#34C759'},
        'NLP': {'icon': '💬', 'color': '#AF52DE'},
        'Computer Vision': {'icon': '👁️', 'color': '#FF9500'}
    }
    
    for idx, category in enumerate(categories):
        with cols[idx % 2]:
            # Get user's progress for this category
            stats = progress_tracker.get_category_stats(category)
            score = stats.get('score', 0)
            answered = stats.get('answered', 0)
            total = stats.get('total', 0)
            
            # Determine level and colors
            if score == 0:
                level = "Not Started"
                level_color = "#AF52DE"
                icon_bg = "linear-gradient(135deg, #AF52DE, #BF5AF2)"
            elif score < 40:
                level = "Beginner"
                level_color = "#FF9500"
                icon_bg = "linear-gradient(135deg, #FF9500, #FFD60A)"
            elif score < 70:
                level = "Junior"
                level_color = "#007AFF"
                icon_bg = "linear-gradient(135deg, #007AFF, #5AC8FA)"
            elif score < 85:
                level = "Middle"
                level_color = "#FFD60A"
                icon_bg = "linear-gradient(135deg, #FFD60A, #FF9500)"
            else:
                level = "Senior"
                level_color = "#34C759"
                icon_bg = "linear-gradient(135deg, #34C759, #30D158)"
            
            info = category_info.get(category, {'icon': '📚', 'color': '#007AFF'})
            
            # Create beautiful skill card
            if st.button(
                f"{info['icon']} {category}",
                key=f"cat_{category}",
                use_container_width=True
            ):
                st.session_state.selected_category = category
                st.session_state.current_question_index = 0
                st.session_state.quiz_answers = []
                st.rerun()
            
            # Display progress info
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                border-left: 4px solid {level_color};
            ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        background: {icon_bg};
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                        font-size: 20px;
                    ">{info['icon']}</div>
                    <div>
                        <div style="font-weight: 600; font-size: 16px;">{category}</div>
                        <div style="
                            background: {level_color}20;
                            color: {level_color};
                            padding: 4px 8px;
                            border-radius: 8px;
                            font-size: 12px;
                            font-weight: 600;
                            display: inline-block;
                        ">{level}</div>
                    </div>
                </div>
                <div style="margin-bottom: 8px; color: #8e8e93; font-size: 12px;">Progress</div>
                <div style="
                    background: #f2f2f7;
                    height: 6px;
                    border-radius: 3px;
                    overflow: hidden;
                ">
                    <div style="
                        background: {level_color};
                        height: 100%;
                        width: {score}%;
                        transition: width 0.3s ease;
                    "></div>
                </div>
                <div style="
                    font-weight: 600;
                    margin-top: 8px;
                    font-size: 14px;
                ">{score:.0f}% • {answered}/{total} вопросов</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show quiz if category is selected
    if 'selected_category' in st.session_state:
        show_category_quiz(st.session_state.selected_category, progress_tracker)


def show_category_quiz(category, progress_tracker):
    """
    Show quiz for selected category
    """
    questions = progress_tracker.get_questions_by_category(category)
    
    if not questions:
        st.error(f"Нет вопросов для категории {category}")
        return
    
    # Initialize quiz state
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = []
    
    current_index = st.session_state.current_question_index
    
    # Check if quiz is completed
    if current_index >= len(questions):
        show_quiz_results(category, progress_tracker)
        return
    
    question = questions[current_index]
    
    # Progress bar
    progress = (current_index + 1) / len(questions)
    st.progress(progress)
    st.markdown(f"**Вопрос {current_index + 1} из {len(questions)}**")
    
    # Question display
    display_assessment_question(question, current_index, category)


def display_assessment_question(question_data, question_index, category):
    """
    Display a single assessment question with enhanced UI
    """
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
    
    # Parse options
    options = question_data['options']
    if isinstance(options, str):
        try:
            options = json.loads(options)
        except:
            options = [options]
    
    # Display options with radio buttons
    selected_option = st.radio(
        "Выберите ответ:",
        options,
        key=f"q_{question_data['id']}",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Submit button
    with col2:
        if st.button("Ответить", type="primary", use_container_width=True):
            handle_answer_submission(selected_option, question_data, category, f"q_{question_data['id']}")
    
    # Hint and AI chat buttons
    with col1:
        if st.button("💡 Подсказка", use_container_width=True):
            if question_data.get('hint'):
                st.info(f"💡 **Подсказка:** {question_data['hint']}")
            else:
                st.warning("Подсказка недоступна для этого вопроса")
    
    with col3:
        if st.button("🤖 Чат с ИИ", use_container_width=True):
            show_ai_explanation(question_data, f"q_{question_data['id']}")


def handle_answer_submission(selected_option, question_data, category, key):
    """
    Handle answer submission and provide feedback
    """
    if not selected_option:
        st.warning("Пожалуйста, выберите ответ")
        return
    
    correct_answer = question_data['correct_answer']
    is_correct = selected_option == correct_answer
    
    # Save answer
    progress_tracker = DatabaseProgressTracker()
    progress_tracker.add_answer(
        question_id=question_data['id'],
        category=category,
        selected_answer=selected_option,
        correct_answer=correct_answer
    )
    
    # Store answer in session
    st.session_state.quiz_answers.append({
        'question_id': question_data['id'],
        'selected': selected_option,
        'correct': correct_answer,
        'is_correct': is_correct
    })
    
    # Show feedback
    if is_correct:
        st.success(f"✅ Правильно! Ответ: {correct_answer}")
    else:
        st.error(f"❌ Неправильно. Правильный ответ: {correct_answer}")
    
    # Move to next question
    if st.button("Следующий вопрос"):
        st.session_state.current_question_index += 1
        st.rerun()


def show_ai_explanation(question_data, key):
    """
    Get and display AI explanation for a question
    """
    with st.expander("🤖 ИИ-объяснение", expanded=True):
        try:
            options = question_data['options']
            if isinstance(options, str):
                options = json.loads(options)
            
            explanation = get_ai_explanation(
                question_data['question_text'],
                options,
                question_data['correct_answer']
            )
            st.markdown(explanation)
        except Exception as e:
            st.error(f"Ошибка получения объяснения: {e}")


def show_quiz_results(category, progress_tracker):
    """
    Show quiz completion results
    """
    stats = progress_tracker.get_category_stats(category)
    score = stats.get('score', 0)
    
    # Determine level
    if score >= 85:
        level = "Senior"
        emoji = "🏆"
        color = "#34C759"
    elif score >= 70:
        level = "Middle"
        emoji = "🥈"
        color = "#FFD60A"
    elif score >= 40:
        level = "Junior"
        emoji = "🥉"
        color = "#007AFF"
    else:
        level = "Beginner"
        emoji = "📚"
        color = "#FF9500"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, {color}80 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 30px 0;
    ">
        <div style="font-size: 60px; margin-bottom: 20px;">{emoji}</div>
        <h1 style="margin: 0; font-size: 32px;">Тест завершен!</h1>
        <h2 style="margin: 10px 0; font-size: 24px;">Уровень: {level}</h2>
        <h3 style="margin: 10px 0; font-size: 20px;">Результат: {score:.1f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Show detailed results
    correct_count = len([a for a in st.session_state.quiz_answers if a['is_correct']])
    total_count = len(st.session_state.quiz_answers)
    
    st.markdown(f"""
    ### 📊 Детальные результаты
    - **Правильных ответов:** {correct_count} из {total_count}
    - **Процент успеха:** {score:.1f}%
    - **Категория:** {category}
    - **Ваш уровень:** {level} {emoji}
    """)
    
    if st.button("Начать заново", type="primary"):
        # Clear quiz state
        if 'selected_category' in st.session_state:
            del st.session_state.selected_category
        if 'current_question_index' in st.session_state:
            del st.session_state.current_question_index
        if 'quiz_answers' in st.session_state:
            del st.session_state.quiz_answers
        st.rerun()