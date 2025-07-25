"""
Database-backed progress tracker for Interview Prep app
Uses SQLite database for persistent storage
"""
import json
from datetime import datetime
from typing import Dict, List
import streamlit as st
from utils.database import db_manager

class DatabaseProgressTracker:
    """
    Database-backed progress tracker for persistent user progress
    """
    
    def __init__(self, session_id: str = None):
        if session_id is None:
            # Use Streamlit session ID or create one
            if 'session_id' not in st.session_state:
                import uuid
                st.session_state.session_id = str(uuid.uuid4())
            session_id = st.session_state.session_id
        
        self.session_id = session_id
        self.user_id = db_manager.get_or_create_user(session_id)
        
        # Initialize database tables if needed
        try:
            db_manager.create_tables()
        except Exception as e:
            st.error(f"Database initialization error: {e}")
    
    def add_answer(self, question_id: int, category: str, selected_answer: str, correct_answer: str):
        """
        Add an answer to the database
        
        Args:
            question_id (int): The ID of the question
            category (str): The category of the question
            selected_answer (str): User's selected answer
            correct_answer (str): The correct answer
        """
        is_correct = selected_answer == correct_answer
        db_manager.save_user_answer(
            user_id=self.user_id,
            question_id=question_id,
            category=category,
            selected_answer=selected_answer,
            is_correct=is_correct
        )
    
    def get_category_stats(self, category: str) -> Dict:
        """
        Get statistics for a specific category
        
        Args:
            category (str): The category name
            
        Returns:
            Dict: Category statistics
        """
        return db_manager.get_category_stats(self.user_id, category)
    
    def get_subcategory_stats(self, category: str, subcategory: str) -> Dict:
        """
        Get statistics for a specific subcategory
        
        Args:
            category (str): The category name
            subcategory (str): The subcategory name
            
        Returns:
            Dict: Subcategory statistics
        """
        return db_manager.get_subcategory_stats(self.user_id, category, subcategory)
    
    def get_overall_score(self) -> float:
        """
        Get the overall score percentage
        
        Returns:
            float: Overall score as percentage
        """
        progress = db_manager.get_user_progress(self.user_id)
        return progress.get('overall_score', 0.0)
    
    def get_total_questions_answered(self) -> int:
        """
        Get the total number of questions answered
        
        Returns:
            int: Total questions answered
        """
        progress = db_manager.get_user_progress(self.user_id)
        return progress.get('total_questions', 0)
    
    def get_weak_areas(self, threshold: float = 60.0) -> List[str]:
        """
        Get categories where the user scored below the threshold
        
        Args:
            threshold (float): Score threshold (default 60%)
            
        Returns:
            List[str]: List of weak category names
        """
        progress = db_manager.get_user_progress(self.user_id)
        weak_areas = []
        
        for category, stats in progress.get('categories', {}).items():
            if stats['score'] < threshold:
                weak_areas.append(category)
        
        return weak_areas
    
    def get_strong_areas(self, threshold: float = 80.0) -> List[str]:
        """
        Get categories where the user scored above the threshold
        
        Args:
            threshold (float): Score threshold (default 80%)
            
        Returns:
            List[str]: List of strong category names
        """
        progress = db_manager.get_user_progress(self.user_id)
        strong_areas = []
        
        for category, stats in progress.get('categories', {}).items():
            if stats['score'] >= threshold:
                strong_areas.append(category)
        
        return strong_areas
    
    def get_recent_performance(self, limit: int = 10) -> List[Dict]:
        """
        Get recent answer history
        
        Args:
            limit (int): Number of recent answers to return
            
        Returns:
            List[Dict]: Recent answers
        """
        return db_manager.get_user_answers_history(self.user_id, limit)
    
    def get_category_progress_summary(self) -> Dict:
        """
        Get a summary of progress across all categories
        
        Returns:
            Dict: Progress summary
        """
        progress = db_manager.get_user_progress(self.user_id)
        categories = progress.get('categories', {})
        
        summary = {
            'total_categories_attempted': len(categories),
            'categories': {}
        }
        
        for category, stats in categories.items():
            score = stats['score']
            
            # Determine level
            if score >= 80:
                level = "Senior"
                level_emoji = "🏆"
            elif score >= 60:
                level = "Middle"
                level_emoji = "🥈"
            else:
                level = "Junior"
                level_emoji = "🥉"
            
            summary['categories'][category] = {
                'score': round(score, 1),
                'level': level,
                'level_emoji': level_emoji,
                'questions_answered': stats['total'],
                'correct_answers': stats['correct']
            }
        
        return summary
    
    def reset_progress(self):
        """
        Reset all progress data for the current user
        """
        # This would require additional database methods to delete user data
        # For now, we'll just create a new session
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
        self.session_id = st.session_state.session_id
        self.user_id = db_manager.get_or_create_user(self.session_id)
    
    def export_progress(self) -> str:
        """
        Export progress as JSON string
        
        Returns:
            str: JSON representation of progress
        """
        import json
        progress = db_manager.get_user_progress(self.user_id)
        return json.dumps(progress, indent=2)
    
    def get_all_categories(self) -> List[str]:
        """
        Get all available categories from database
        
        Returns:
            List[str]: List of category names
        """
        return db_manager.get_all_categories()
    
    def get_questions_by_category(self, category: str) -> List[Dict]:
        """
        Get all questions for a specific category
        
        Args:
            category (str): Category name
            
        Returns:
            List[Dict]: List of questions with their data
        """
        return db_manager.get_questions_by_category(category)