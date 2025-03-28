from bson import ObjectId
from datetime import datetime

class NutritionalInfo:
    """
    NutritionalInfo class for storing details on meal calories, macronutrients, and dietary categorization.
    """
    def __init__(self, calories, protein, carbs, fat, dietary_tags=None):
        self.calories = calories
        self.protein = protein  # in grams
        self.carbs = carbs      # in grams
        self.fat = fat          # in grams
        self.dietary_tags = dietary_tags if dietary_tags else []
    
    def to_dict(self):
        """Convert nutritional info to dictionary"""
        return {
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "dietary_tags": self.dietary_tags
        }
    
    @classmethod
    def from_dict(cls, nutrition_dict):
        """Create a NutritionalInfo object from a dictionary"""
        if not nutrition_dict:
            return None
        
        return cls(
            calories=nutrition_dict.get("calories", 0),
            protein=nutrition_dict.get("protein", 0),
            carbs=nutrition_dict.get("carbs", 0),
            fat=nutrition_dict.get("fat", 0),
            dietary_tags=nutrition_dict.get("dietary_tags", [])
        )


class Meal:
    """
    Meal class for defining meal properties, including name, ingredients, recipe, and nutritional info.
    """
    def __init__(self, name, ingredients, recipe_steps, meal_id=None, image_url=None, 
                 prep_time=None, cook_time=None, servings=None, cuisine_type=None, 
                 meal_type=None, nutritional_info=None, mood_tags=None, created_at=None):
        self.meal_id = meal_id if meal_id else ObjectId()
        self.name = name
        self.ingredients = ingredients
        self.recipe_steps = recipe_steps
        self.image_url = image_url
        self.prep_time = prep_time  # in minutes
        self.cook_time = cook_time  # in minutes
        self.servings = servings
        self.cuisine_type = cuisine_type
        self.meal_type = meal_type  # breakfast, lunch, dinner, snack
        self.nutritional_info = nutritional_info
        self.mood_tags = mood_tags if mood_tags else []
        self.created_at = created_at if created_at else datetime.now()
    
    def total_time(self):
        """Calculate total preparation and cooking time"""
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook
    
    def to_dict(self):
        """Convert meal object to dictionary for database storage"""
        return {
            "_id": self.meal_id,
            "name": self.name,
            "ingredients": self.ingredients,
            "recipe_steps": self.recipe_steps,
            "image_url": self.image_url,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "servings": self.servings,
            "cuisine_type": self.cuisine_type,
            "meal_type": self.meal_type,
            "nutritional_info": self.nutritional_info.to_dict() if self.nutritional_info else None,
            "mood_tags": self.mood_tags,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, meal_dict):
        """Create a Meal object from a dictionary"""
        if not meal_dict:
            return None
        
        nutritional_info = None
        if meal_dict.get("nutritional_info"):
            nutritional_info = NutritionalInfo.from_dict(meal_dict.get("nutritional_info"))
        
        return cls(
            name=meal_dict.get("name"),
            ingredients=meal_dict.get("ingredients", []),
            recipe_steps=meal_dict.get("recipe_steps", []),
            meal_id=meal_dict.get("_id"),
            image_url=meal_dict.get("image_url"),
            prep_time=meal_dict.get("prep_time"),
            cook_time=meal_dict.get("cook_time"),
            servings=meal_dict.get("servings"),
            cuisine_type=meal_dict.get("cuisine_type"),
            meal_type=meal_dict.get("meal_type"),
            nutritional_info=nutritional_info,
            mood_tags=meal_dict.get("mood_tags", []),
            created_at=meal_dict.get("created_at")
        )
