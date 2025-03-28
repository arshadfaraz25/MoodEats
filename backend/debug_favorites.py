from flask import Flask, session
from pymongo import MongoClient
from bson import ObjectId
import json
import traceback

# Custom JSON encoder to handle ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

# Get current user from session
def debug_get_favorites():
    """Simulate the get_favorites route to debug the issue"""
    try:
        # Get all users to test with
        users = list(db.users.find())
        
        if not users:
            print("No users found in the database")
            return
        
        # Use the first user for testing
        user_id = users[0]['_id']
        print(f"Testing with user ID: {user_id}")
        
        # Get user preferences
        user_prefs = db.user_preferences.find_one({"user_id": user_id})
        
        # If user has no preferences yet, return empty array
        if not user_prefs:
            print(f"User {user_id} has no preferences yet")
            return []
        
        print(f"User preferences found: {json.dumps(user_prefs, cls=MongoJSONEncoder)}")
        
        # Get favorite meals
        favorite_meals = []
        for meal_id in user_prefs.get('favorite_meals', []):
            try:
                print(f"Processing favorite meal ID: {meal_id}")
                if isinstance(meal_id, str):
                    meal_id = ObjectId(meal_id)
                
                meal_dict = db.meals.find_one({"_id": meal_id})
                if meal_dict:
                    print(f"Found meal: {meal_dict.get('name')}")
                    # Convert all ObjectId values in meal to strings
                    for key, value in meal_dict.items():
                        if isinstance(value, ObjectId):
                            meal_dict[key] = str(value)
                        elif isinstance(value, list):
                            # Handle lists that might contain ObjectId values
                            for i, item in enumerate(value):
                                if isinstance(item, ObjectId):
                                    value[i] = str(item)
                        elif isinstance(value, dict):
                            # Handle nested dictionaries
                            for k, v in value.items():
                                if isinstance(v, ObjectId):
                                    value[k] = str(v)
                    
                    favorite_meals.append(meal_dict)
                else:
                    print(f"Meal not found for ID: {meal_id}")
            except Exception as e:
                print(f"Error processing meal {meal_id}: {str(e)}")
                traceback.print_exc()
        
        print(f"Found {len(favorite_meals)} favorite meals for user {user_id}")
        return favorite_meals
    except Exception as e:
        print(f"Error in get_favorites: {str(e)}")
        traceback.print_exc()
        return None

# Run the debug function
result = debug_get_favorites()
print("\nResult:")
if result is not None:
    print(json.dumps(result, cls=MongoJSONEncoder, indent=2))
else:
    print("Error occurred during debugging")
