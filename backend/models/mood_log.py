"""
File name: mood_log.py
Purpose: Defines the MoodLog model for tracking user mood entries in the MoodEats application.
         Used for mood-based meal recommendations and user history tracking.

@author Arshad Faraz
@version 1.0.0
"""
from datetime import datetime
from bson import ObjectId

class MoodLog:
    """
    MoodLog class for storing user mood selections and interactions for recommendation improvements.
    """
    def __init__(self, user_id, mood, timestamp=None, log_id=None, notes=None, related_meals=None):
        self.log_id = log_id if log_id else ObjectId()
        self.user_id = user_id
        self.mood = mood
        self.timestamp = timestamp if timestamp else datetime.now()
        self.notes = notes
        self.related_meals = related_meals if related_meals else []
    
    def add_related_meal(self, meal_id):
        """Add a meal ID to the related meals list"""
        if meal_id not in self.related_meals:
            self.related_meals.append(meal_id)
    
    def to_dict(self):
        """Convert mood log object to dictionary for database storage"""
        return {
            "_id": self.log_id,
            "user_id": self.user_id,
            "mood": self.mood,
            "timestamp": self.timestamp,
            "notes": self.notes,
            "related_meals": self.related_meals
        }
    
    @classmethod
    def from_dict(cls, mood_log_dict):
        """Create a MoodLog object from a dictionary"""
        if not mood_log_dict:
            return None
        
        return cls(
            user_id=mood_log_dict.get("user_id"),
            mood=mood_log_dict.get("mood"),
            timestamp=mood_log_dict.get("timestamp"),
            log_id=mood_log_dict.get("_id"),
            notes=mood_log_dict.get("notes"),
            related_meals=mood_log_dict.get("related_meals", [])
        )
