from flask import Flask, session
from pymongo import MongoClient
from bson import ObjectId
import json
import datetime

# Custom JSON encoder to handle ObjectId and datetime
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

# User ID to test with
user_id_str = "67e5b44627a9382198557540"
user_id = ObjectId(user_id_str)

# Get user preferences
user_prefs = db.user_preferences.find_one({"user_id": user_id})
if not user_prefs:
    print(f"User {user_id_str} has no preferences yet")
    exit(1)

print(f"User preferences found with ID: {user_prefs.get('_id')}")
print(f"Favorite meals IDs: {user_prefs.get('favorite_meals', [])}")

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
            # Convert ObjectId to string for JSON serialization
            meal_dict['_id'] = str(meal_dict['_id'])
            
            # Convert other ObjectId values in meal to strings
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
        import traceback
        traceback.print_exc()

print(f"Found {len(favorite_meals)} favorite meals")

# Print favorite meals
for i, meal in enumerate(favorite_meals):
    print(f"\nFavorite Meal #{i+1}:")
    print(f"ID: {meal.get('_id')}")
    print(f"Name: {meal.get('name')}")
    print(f"Description: {meal.get('description')[:50]}..." if meal.get('description') else "Description: None")
    print(f"Cuisine: {meal.get('cuisine_type')}")
    print(f"Mood Tags: {meal.get('mood_tags')}")

# Save to JSON file for frontend testing
with open('favorite_meals.json', 'w') as f:
    json.dump(favorite_meals, f, cls=MongoJSONEncoder, indent=2)

print("\nFavorite meals saved to favorite_meals.json")
print("Done!")
