"""
File name: check_db.py
Purpose: Script to check the MongoDB database content for MoodEats.
         Prints counts of documents in each collection.

@author Cascade
@version 1.0.0
"""
from pymongo import MongoClient
from datetime import datetime, timedelta
import sys
import os

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

def check_database_content():
    """
    Check the content of the database and print counts
    """
    print("\n=== MoodEats Database Content Check ===\n")
    
    # Check users collection
    user_count = db.users.count_documents({})
    admin_count = db.users.count_documents({"is_admin": True})
    print(f"Users: {user_count} (including {admin_count} admins)")
    
    # Check meals collection
    meal_count = db.meals.count_documents({})
    print(f"Meals: {meal_count}")
    
    # Check mood_logs collection
    mood_log_count = db.mood_logs.count_documents({})
    
    # Check today's mood logs
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    today_logs_count = db.mood_logs.count_documents({
        "timestamp": {
            "$gte": today,
            "$lt": tomorrow
        }
    })
    
    print(f"Mood Logs: {mood_log_count} (including {today_logs_count} from today)")
    
    # Check user_preferences collection
    pref_count = db.user_preferences.count_documents({})
    print(f"User Preferences: {pref_count}")
    
    # Check feedback collection
    feedback_count = db.feedback.count_documents({})
    print(f"Feedback entries: {feedback_count}")
    
    # Print some sample data if available
    print("\n=== Sample Data ===\n")
    
    # Sample user
    sample_user = db.users.find_one({}, {"password_hash": 0})
    if sample_user:
        print(f"Sample User: {sample_user}")
    else:
        print("No users found")
    
    # Sample meal
    sample_meal = db.meals.find_one({})
    if sample_meal:
        print(f"\nSample Meal: {sample_meal}")
    else:
        print("\nNo meals found")
    
    # Sample mood log
    sample_mood_log = db.mood_logs.find_one({})
    if sample_mood_log:
        print(f"\nSample Mood Log: {sample_mood_log}")
    else:
        print("\nNo mood logs found")

if __name__ == "__main__":
    check_database_content()
