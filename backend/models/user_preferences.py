from bson import ObjectId

class UserPreferences:
    """
    UserPreferences class for tracking user settings such as dietary restrictions, 
    cuisines, and calorie goals.
    """
    def __init__(self, user_id, preferences_id=None, dietary_restrictions=None, 
                 cuisines=None, calorie_goal=None, address=None, 
                 allergies=None, favorite_meals=None):
        self.preferences_id = preferences_id if preferences_id else ObjectId()
        self.user_id = user_id
        self.dietary_restrictions = dietary_restrictions if dietary_restrictions else []
        self.cuisines = cuisines if cuisines else []
        self.calorie_goal = calorie_goal
        self.address = address
        self.allergies = allergies if allergies else []
        self.favorite_meals = favorite_meals if favorite_meals else []
    
    def add_favorite_meal(self, meal_id):
        """Add a meal to favorites"""
        if meal_id not in self.favorite_meals:
            self.favorite_meals.append(meal_id)
    
    def remove_favorite_meal(self, meal_id):
        """Remove a meal from favorites"""
        if meal_id in self.favorite_meals:
            self.favorite_meals.remove(meal_id)
    
    def to_dict(self):
        """Convert user preferences object to dictionary for database storage"""
        return {
            "_id": self.preferences_id,
            "user_id": self.user_id,
            "dietary_restrictions": self.dietary_restrictions,
            "cuisines": self.cuisines,
            "calorie_goal": self.calorie_goal,
            "address": self.address,
            "allergies": self.allergies,
            "favorite_meals": self.favorite_meals
        }
    
    @classmethod
    def from_dict(cls, preferences_dict):
        """Create a UserPreferences object from a dictionary"""
        if not preferences_dict:
            return None
        
        return cls(
            user_id=preferences_dict.get("user_id"),
            preferences_id=preferences_dict.get("_id"),
            dietary_restrictions=preferences_dict.get("dietary_restrictions", []),
            cuisines=preferences_dict.get("cuisines", []),
            calorie_goal=preferences_dict.get("calorie_goal"),
            address=preferences_dict.get("address"),
            allergies=preferences_dict.get("allergies", []),
            favorite_meals=preferences_dict.get("favorite_meals", [])
        )
