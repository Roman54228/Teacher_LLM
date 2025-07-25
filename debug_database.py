#!/usr/bin/env python3
import sqlite3
import json

# Connect to SQLite database
conn = sqlite3.connect('interview_prep.db')
cursor = conn.cursor()

print("=== DEBUGGING DATABASE ===")

# Check user_answers table for Screening Test
print("\n1. Checking user_answers for Screening Test:")
cursor.execute("SELECT * FROM user_answers WHERE category = 'Screening Test' ORDER BY answered_at DESC LIMIT 5")
answers = cursor.fetchall()
print(f"Found {len(answers)} answers in Screening Test category:")
for answer in answers:
    print(f"  ID: {answer[0]}, User: {answer[1]}, Question: {answer[2]}, Category: {answer[3]}, Correct: {answer[5]}")

# Check user_progress table for Screening Test
print("\n2. Checking user_progress for Screening Test:")
cursor.execute("SELECT * FROM user_progress WHERE category = 'Screening Test'")
progress = cursor.fetchall()
print(f"Found {len(progress)} progress records for Screening Test:")
for record in progress:
    print(f"  User: {record[1]}, Total: {record[3]}, Correct: {record[4]}, Score: {record[5]}%, Level: {record[6]}")

# Check all categories in user_answers
print("\n3. All categories in user_answers:")
cursor.execute("SELECT DISTINCT category FROM user_answers")
categories = cursor.fetchall()
print("Categories:", [cat[0] for cat in categories])

# Check recent answers
print("\n4. Recent 10 answers (all categories):")
cursor.execute("SELECT user_id, question_id, category, is_correct, answered_at FROM user_answers ORDER BY answered_at DESC LIMIT 10")
recent = cursor.fetchall()
for record in recent:
    print(f"  User: {record[0][:8]}..., Q{record[1]}, {record[2]}, Correct: {record[3]}, Time: {record[4]}")

conn.close()