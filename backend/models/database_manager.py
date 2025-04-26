"""
File name: database_manager.py
Purpose: Centralized database manager for MoodEats application.
         Handles all database operations for users, meals, mood logs, and feedback.

@author Arshad Faraz
@version 1.0.0
"""
from bson import ObjectId
import random
from models.user import User
from models.meal import Meal, NutritionalInfo
from models.mood_log import MoodLog
from models.feedback import Feedback
from models.user_preferences import UserPreferences

class DatabaseManager:
    """
    DatabaseManager class for centralized storage of users, meals, moods, and feedback data.
    """
    def __init__(self, mongo_client):
        self.db = mongo_client.db
    
    # User operations
    def create_user(self, user):
        """Create a new user in the database"""
        user_dict = user.to_dict()
        result = self.db.users.insert_one(user_dict)
        return result.inserted_id
    
    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        user_dict = self.db.users.find_one({"_id": ObjectId(user_id)})
        return User.from_dict(user_dict) if user_dict else None
    
    def get_user_by_email(self, email):
        """Get a user by email"""
        user_dict = self.db.users.find_one({"email": email})
        return User.from_dict(user_dict) if user_dict else None
    
    def update_user(self, user):
        """Update a user in the database"""
        user_dict = user.to_dict()
        self.db.users.update_one(
            {"_id": user.user_id},
            {"$set": user_dict}
        )
    
    def delete_user(self, user_id):
        """Delete a user from the database"""
        self.db.users.delete_one({"_id": ObjectId(user_id)})
        # Also delete related data
        self.db.user_preferences.delete_many({"user_id": ObjectId(user_id)})
        self.db.mood_logs.delete_many({"user_id": ObjectId(user_id)})
        self.db.feedback.delete_many({"user_id": ObjectId(user_id)})
    
    # Meal operations
    def create_meal(self, meal):
        """Create a new meal in the database"""
        meal_dict = meal.to_dict()
        result = self.db.meals.insert_one(meal_dict)
        return result.inserted_id
    
    def get_meal_by_id(self, meal_id):
        """Get a meal by ID"""
        meal_dict = self.db.meals.find_one({"_id": ObjectId(meal_id)})
        return Meal.from_dict(meal_dict) if meal_dict else None
    
    def get_meals_by_ids(self, meal_ids):
        """Get multiple meals by their IDs"""
        object_ids = [ObjectId(mid) for mid in meal_ids]
        meal_dicts = self.db.meals.find({"_id": {"$in": object_ids}})
        return [Meal.from_dict(meal_dict) for meal_dict in meal_dicts]
    
    def get_meals_by_query(self, query, limit=10):
        """Get meals based on a query"""
        meal_dicts = self.db.meals.find(query).limit(limit)
        return [Meal.from_dict(meal_dict) for meal_dict in meal_dicts]
    
    def get_random_meals(self, limit=10):
        """Get random meals from the database"""
        # MongoDB aggregation to get random documents
        pipeline = [{"$sample": {"size": limit}}]
        meal_dicts = self.db.meals.aggregate(pipeline)
        return [Meal.from_dict(meal_dict) for meal_dict in meal_dicts]
    
    def update_meal(self, meal):
        """Update a meal in the database"""
        meal_dict = meal.to_dict()
        self.db.meals.update_one(
            {"_id": meal.meal_id},
            {"$set": meal_dict}
        )
    
    def delete_meal(self, meal_id):
        """Delete a meal from the database"""
        self.db.meals.delete_one({"_id": ObjectId(meal_id)})
    
    # Mood log operations
    def create_mood_log(self, user_id, mood, notes=None):
        """Create a new mood log entry"""
        mood_log = MoodLog(
            user_id=ObjectId(user_id),
            mood=mood,
            notes=notes
        )
        mood_log_dict = mood_log.to_dict()
        result = self.db.mood_logs.insert_one(mood_log_dict)
        return result.inserted_id
    
    def get_mood_logs_by_user(self, user_id, limit=10):
        """Get mood logs for a specific user"""
        mood_log_dicts = self.db.mood_logs.find(
            {"user_id": ObjectId(user_id)}
        ).sort("timestamp", -1).limit(limit)
        
        return [MoodLog.from_dict(log_dict) for log_dict in mood_log_dicts]
    
    # Feedback operations
    def create_feedback(self, feedback):
        """Create a new feedback entry"""
        feedback_dict = feedback.to_dict()
        result = self.db.feedback.insert_one(feedback_dict)
        return result.inserted_id
    
    def get_user_feedback(self, user_id, limit=10):
        """Get feedback for a specific user"""
        feedback_dicts = self.db.feedback.find(
            {"user_id": ObjectId(user_id)}
        ).sort("timestamp", -1).limit(limit)
        
        return [Feedback.from_dict(f_dict) for f_dict in feedback_dicts]
    
    def get_meal_feedback(self, meal_id, limit=10):
        """Get feedback for a specific meal"""
        feedback_dicts = self.db.feedback.find(
            {"meal_id": ObjectId(meal_id)}
        ).sort("timestamp", -1).limit(limit)
        
        return [Feedback.from_dict(f_dict) for f_dict in feedback_dicts]
    
    # User preferences operations
    def create_user_preferences(self, preferences):
        """Create new user preferences"""
        prefs_dict = preferences.to_dict()
        result = self.db.user_preferences.insert_one(prefs_dict)
        return result.inserted_id
    
    def get_user_preferences(self, user_id):
        """Get preferences for a specific user"""
        prefs_dict = self.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
        return UserPreferences.from_dict(prefs_dict) if prefs_dict else None
    
    def update_user_preferences(self, preferences):
        """Update user preferences"""
        prefs_dict = preferences.to_dict()
        self.db.user_preferences.update_one(
            {"user_id": ObjectId(preferences.user_id)},
            {"$set": prefs_dict},
            upsert=True
        )
    
    # Admin operations
    def get_all_users(self, limit=100):
        """Get all users (for admin purposes)"""
        user_dicts = self.db.users.find().limit(limit)
        return [User.from_dict(user_dict) for user_dict in user_dicts]
    
    def get_all_meals(self, limit=100):
        """Get all meals (for admin purposes)"""
        meal_dicts = self.db.meals.find().limit(limit)
        return [Meal.from_dict(meal_dict) for meal_dict in meal_dicts]
    
    def bulk_insert_meals(self, meals):
        """Insert multiple meals at once (for admin purposes)"""
        meal_dicts = [meal.to_dict() for meal in meals]
        result = self.db.meals.insert_many(meal_dicts)
        return result.inserted_ids
