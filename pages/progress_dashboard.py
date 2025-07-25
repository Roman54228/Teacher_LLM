"""
Progress Dashboard for Interview Prep
Enhanced with beautiful visualizations and AI recommendations
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.db_progress_tracker import DatabaseProgressTracker
from utils.yandex_gpt_helper import get_personalized_recommendations


def show_progress_dashboard():
    """
    Display comprehensive progress dashboard
    """
    progress_tracker = DatabaseProgressTracker()
    
    # Check if user has any progress
    total_answered = progress_tracker.get_total_questions_answered()
    
    if total_answered == 0:
        show_empty_dashboard()
        return
    
    # Header with gradient design
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #34C759 0%, #30D158 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    ">
        <h1 style="margin: 0; font-size: 32px; font-weight: 700;">📈 Progress Dashboard</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Ваш прогресс в изучении</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Overview metrics
    show_overview_metrics()
    
    # Performance charts
    show_performance_charts()
    
    # Detailed analysis
    show_detailed_analysis()
    
    # AI recommendations
    show_ai_recommendations()


def show_empty_dashboard():
    """
    Show dashboard for users with no progress
    """
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #007AFF 0%, #0056cc 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 30px 0;
    ">
        <div style="font-size: 60px; margin-bottom: 20px;">🎯</div>
        <h1 style="margin: 0; font-size: 28px;">Начните свое обучение!</h1>
        <p style="margin: 15px 0; font-size: 16px; opacity: 0.9;">
            Пройдите первый тест, чтобы увидеть свой прогресс здесь
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Начать тестирование", type="primary", use_container_width=True):
        st.switch_page("pages/skill_assessment.py")


def show_overview_metrics():
    """
    Display overview metrics in an organized layout
    """
    progress_tracker = DatabaseProgressTracker()
    
    # Get overall statistics
    overall_score = progress_tracker.get_overall_score()
    total_answered = progress_tracker.get_total_questions_answered()
    
    # Determine overall level
    if overall_score >= 85:
        level = "Senior"
        level_emoji = "🏆"
        level_color = "#34C759"
    elif overall_score >= 70:
        level = "Middle"
        level_emoji = "🥈"
        level_color = "#FFD60A"
    elif overall_score >= 40:
        level = "Junior"
        level_emoji = "🥉"
        level_color = "#007AFF"
    else:
        level = "Beginner"
        level_emoji = "📚"
        level_color = "#FF9500"
    
    # Display metrics in cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border-left: 4px solid {level_color};
        ">
            <div style="font-size: 40px; margin-bottom: 10px;">{level_emoji}</div>
            <div style="font-size: 18px; font-weight: 600; color: #1d1d1f;">Текущий уровень</div>
            <div style="font-size: 24px; font-weight: 700; color: {level_color}; margin-top: 5px;">{level}</div>
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


def show_performance_charts():
    """
    Display performance charts and visualizations
    """
    st.markdown("### 📊 Анализ по категориям")
    
    progress_tracker = DatabaseProgressTracker()
    categories = progress_tracker.get_all_categories()
    
    if not categories:
        st.warning("Нет данных для отображения")
        return
    
    # Prepare data for charts
    category_data = []
    for category in categories:
        stats = progress_tracker.get_category_stats(category)
        category_data.append({
            'Category': category,
            'Score': stats.get('score', 0),
            'Answered': stats.get('answered', 0),
            'Total': stats.get('total', 0)
        })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scores by category
        if category_data:
            scores_fig = px.bar(
                category_data,
                x='Category',
                y='Score',
                title='Результаты по категориям',
                color='Score',
                color_continuous_scale='Viridis'
            )
            scores_fig.update_layout(
                xaxis_title="Категория",
                yaxis_title="Балл (%)",
                showlegend=False
            )
            st.plotly_chart(scores_fig, use_container_width=True)
    
    with col2:
        # Progress by category (pie chart)
        if category_data:
            progress_fig = px.pie(
                category_data,
                values='Answered',
                names='Category',
                title='Распределение отвеченных вопросов'
            )
            st.plotly_chart(progress_fig, use_container_width=True)


def show_detailed_analysis():
    """
    Show detailed performance analysis
    """
    st.markdown("### 🔍 Детальный анализ")
    
    progress_tracker = DatabaseProgressTracker()
    
    # Get weak and strong areas
    weak_areas = progress_tracker.get_weak_areas(threshold=60.0)
    strong_areas = progress_tracker.get_strong_areas(threshold=80.0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💪 Сильные стороны")
        if strong_areas:
            for area in strong_areas:
                stats = progress_tracker.get_category_stats(area)
                st.markdown(f"""
                <div style="
                    background: #e8f5e8;
                    border-left: 4px solid #34C759;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                ">
                    <strong>{area}</strong><br>
                    <span style="color: #34C759;">✅ {stats.get('score', 0):.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Продолжайте изучение для выявления сильных сторон")
    
    with col2:
        st.markdown("#### 🎯 Области для улучшения")
        if weak_areas:
            for area in weak_areas:
                stats = progress_tracker.get_category_stats(area)
                st.markdown(f"""
                <div style="
                    background: #fff3e0;
                    border-left: 4px solid #FF9500;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                ">
                    <strong>{area}</strong><br>
                    <span style="color: #FF9500;">📈 {stats.get('score', 0):.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Отличная работа! Все области показывают хорошие результаты")


def show_ai_recommendations():
    """
    Show AI-powered personalized recommendations
    """
    st.markdown("### 🤖 ИИ-рекомендации")
    
    progress_tracker = DatabaseProgressTracker()
    
    # Get user progress data
    user_progress = progress_tracker.get_category_progress_summary()
    weak_areas = progress_tracker.get_weak_areas()
    
    try:
        # Get AI recommendations
        recommendations = get_personalized_recommendations(user_progress, weak_areas)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #AF52DE 0%, #BF5AF2 100%);
            padding: 25px;
            border-radius: 16px;
            color: white;
            margin: 20px 0;
        ">
            <h4 style="margin: 0 0 15px 0;">🎯 Персональные рекомендации</h4>
            <div style="font-size: 16px; line-height: 1.6;">
                {recommendations}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.warning("Рекомендации временно недоступны")
        
        # Show fallback recommendations
        fallback_recommendations = [
            "📚 Изучите основы Python для улучшения результатов",
            "🤖 Практикуйте алгоритмы машинного обучения",
            "💬 Углубитесь в изучение NLP технологий",
            "👁️ Изучите компьютерное зрение и обработку изображений"
        ]
        
        for rec in fallback_recommendations:
            st.markdown(f"- {rec}")


def export_progress_report():
    """
    Export progress as a downloadable report
    """
    progress_tracker = DatabaseProgressTracker()
    
    # Generate report data
    report_data = {
        'overall_score': progress_tracker.get_overall_score(),
        'total_answered': progress_tracker.get_total_questions_answered(),
        'categories': progress_tracker.get_category_progress_summary(),
        'recent_performance': progress_tracker.get_recent_performance()
    }
    
    return report_data