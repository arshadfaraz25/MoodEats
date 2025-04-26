"""
File name: feedback.py
Purpose: Defines the Feedback model for user ratings and comments on meals.
         Used to improve recommendations and track user satisfaction.

@author Arshad Faraz
@version 1.0.0
"""
from datetime import datetime
from bson import ObjectId

class Feedback:
    """
    Feedback class for handling user feedback and ratings for meal recommendations.
    """
    def __init__(self, user_id, meal_id, rating, feedback_id=None, comment=None, 
                 mood_id=None, timestamp=None):
        self.feedback_id = feedback_id if feedback_id else ObjectId()
        self.user_id = user_id
        self.meal_id = meal_id
        self.rating = rating  # Scale of 1-5
        self.comment = comment
        self.mood_id = mood_id  # Optional reference to the mood log
        self.timestamp = timestamp if timestamp else datetime.now()
    
    def to_dict(self):
        """Convert feedback object to dictionary for database storage"""
        return {
            "_id": self.feedback_id,
            "user_id": self.user_id,
            "meal_id": self.meal_id,
            "rating": self.rating,
            "comment": self.comment,
            "mood_id": self.mood_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, feedback_dict):
        """Create a Feedback object from a dictionary"""
        if not feedback_dict:
            return None
        
        return cls(
            user_id=feedback_dict.get("user_id"),
            meal_id=feedback_dict.get("meal_id"),
            rating=feedback_dict.get("rating"),
            feedback_id=feedback_dict.get("_id"),
            comment=feedback_dict.get("comment"),
            mood_id=feedback_dict.get("mood_id"),
            timestamp=feedback_dict.get("timestamp")
        )
