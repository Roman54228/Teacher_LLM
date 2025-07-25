import json
from datetime import datetime
from typing import Dict, List

class ProgressTracker:
    """
    Tracks user progress across different categories and questions
    """
    
    def __init__(self):
        self.progress = {
            'categories': {},
            'session_start': datetime.now().isoformat(),
            'total_questions': 0,
            'total_correct': 0,
            'answers_history': []
        }
    
    def add_answer(self, category: str, is_correct: bool):
        """
        Add an answer to the progress tracker
        
        Args:
            category (str): The category of the question
            is_correct (bool): Whether the answer was correct
        """
        # Initialize category if it doesn't exist
        if category not in self.progress['categories']:
            self.progress['categories'][category] = {
                'total': 0,
                'correct': 0,
                'last_attempt': None
            }
        
        # Update category stats
        self.progress['categories'][category]['total'] += 1
        if is_correct:
            self.progress['categories'][category]['correct'] += 1
        
        self.progress['categories'][category]['last_attempt'] = datetime.now().isoformat()
        
        # Update overall stats
        self.progress['total_questions'] += 1
        if is_correct:
            self.progress['total_correct'] += 1
        
        # Add to history
        self.progress['answers_history'].append({
            'category': category,
            'is_correct': is_correct,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_category_stats(self, category: str) -> Dict:
        """
        Get statistics for a specific category
        
        Args:
            category (str): The category name
            
        Returns:
            Dict: Category statistics
        """
        if category not in self.progress['categories']:
            return {'total': 0, 'correct': 0, 'score': 0.0}
        
        stats = self.progress['categories'][category]
        score = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        
        return {
            'total': stats['total'],
            'correct': stats['correct'],
            'score': score,
            'last_attempt': stats['last_attempt']
        }
    
    def get_overall_score(self) -> float:
        """
        Get the overall score percentage
        
        Returns:
            float: Overall score as percentage
        """
        if self.progress['total_questions'] == 0:
            return 0.0
        
        return (self.progress['total_correct'] / self.progress['total_questions']) * 100
    
    def get_total_questions_answered(self) -> int:
        """
        Get the total number of questions answered
        
        Returns:
            int: Total questions answered
        """
        return self.progress['total_questions']
    
    def get_weak_areas(self, threshold: float = 60.0) -> List[str]:
        """
        Get categories where the user scored below the threshold
        
        Args:
            threshold (float): Score threshold (default 60%)
            
        Returns:
            List[str]: List of weak category names
        """
        weak_areas = []
        
        for category, stats in self.progress['categories'].items():
            if stats['total'] > 0:
                score = (stats['correct'] / stats['total']) * 100
                if score < threshold:
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
        strong_areas = []
        
        for category, stats in self.progress['categories'].items():
            if stats['total'] > 0:
                score = (stats['correct'] / stats['total']) * 100
                if score >= threshold:
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
        return self.progress['answers_history'][-limit:] if self.progress['answers_history'] else []
    
    def get_category_progress_summary(self) -> Dict:
        """
        Get a summary of progress across all categories
        
        Returns:
            Dict: Progress summary
        """
        summary = {
            'total_categories_attempted': len(self.progress['categories']),
            'categories': {}
        }
        
        for category, stats in self.progress['categories'].items():
            score = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            
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
        Reset all progress data
        """
        self.progress = {
            'categories': {},
            'session_start': datetime.now().isoformat(),
            'total_questions': 0,
            'total_correct': 0,
            'answers_history': []
        }
    
    def export_progress(self) -> str:
        """
        Export progress as JSON string
        
        Returns:
            str: JSON representation of progress
        """
        return json.dumps(self.progress, indent=2)
    
    def import_progress(self, progress_json: str):
        """
        Import progress from JSON string
        
        Args:
            progress_json (str): JSON string containing progress data
        """
        try:
            self.progress = json.loads(progress_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for progress data")
