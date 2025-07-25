#!/usr/bin/env python3
import sys
from utils.database import DatabaseManager

# Test database progress tracking
if __name__ == "__main__":
    db_manager = DatabaseManager()
    
    # Test user ID from recent API call
    test_user_id = "7e35e9d8-4e7f-41c0-ac75-ab9b34d0f50f"
    
    print("=== Testing Database Progress ===")
    
    # Test 1: Check if user has answers
    db = db_manager.get_db()
    try:
        from utils.database import UserAnswer, UserProgress
        
        # Count answers
        answer_count = db.query(UserAnswer).filter_by(user_id=test_user_id).count()
        print(f"✓ User has {answer_count} answers in database")
        
        # Show recent answers
        recent_answers = db.query(UserAnswer).filter_by(user_id=test_user_id).limit(3).all()
        for answer in recent_answers:
            print(f"  - Question {answer.question_id}: {answer.selected_answer} (correct: {answer.is_correct})")
        
        # Count progress records  
        progress_count = db.query(UserProgress).filter_by(user_id=test_user_id).count()
        print(f"✓ User has {progress_count} progress records in database")
        
        # Show progress records
        progress_records = db.query(UserProgress).filter_by(user_id=test_user_id).all()
        for progress in progress_records:
            print(f"  - {progress.category}: {progress.correct_answers}/{progress.total_questions} ({progress.score_percentage:.1f}%)")
        
    finally:
        db.close()
    
    # Test 2: Check get_user_progress function
    print("\n=== Testing get_user_progress() ===")
    progress = db_manager.get_user_progress(test_user_id)
    print(f"Progress result: {progress}")
    
    print(f"Total answered: {progress.get('total_answered', 'ERROR')}")
    print(f"Overall score: {progress.get('overall_score', 'ERROR')}")
    print(f"Categories: {progress.get('categories', 'ERROR')}")