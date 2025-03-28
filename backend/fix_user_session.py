from flask import Flask
from flask.sessions import SecureCookieSessionInterface
from pymongo import MongoClient
from bson import ObjectId
import json
import datetime

# Custom JSON encoder to handle ObjectId
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

# User ID to fix
user_id_str = "67e5b44627a9382198557540"
user_id = ObjectId(user_id_str)

# Check if user exists
user = db.users.find_one({"_id": user_id})
if not user:
    print(f"User with ID {user_id_str} not found!")
    exit(1)

print(f"Found user: {user.get('email')}")

# Create a test session for the user
app = Flask(__name__)
app.secret_key = 'dev_key_for_moodeats'  # Same as in app.py
session_interface = SecureCookieSessionInterface()

# Check if user preferences exist
user_prefs = db.user_preferences.find_one({"user_id": user_id})
print(f"User preferences: {json.dumps(user_prefs, cls=MongoJSONEncoder, indent=2)}")

# Print all favorite meals
if user_prefs and 'favorite_meals' in user_prefs:
    print("\nFavorite meals:")
    for meal_id in user_prefs['favorite_meals']:
        meal = db.meals.find_one({"_id": meal_id})
        if meal:
            print(f"- {meal.get('name')} (ID: {meal_id})")
        else:
            print(f"- Unknown meal (ID: {meal_id})")
else:
    print("No favorite meals found")

# Add a test meal to favorites if needed
if not user_prefs or 'favorite_meals' not in user_prefs or len(user_prefs['favorite_meals']) == 0:
    # Get a random meal
    meal = db.meals.find_one()
    if meal:
        print(f"\nAdding test meal to favorites: {meal.get('name')} (ID: {meal['_id']})")
        
        if not user_prefs:
            # Create new user preferences
            new_prefs = {
                "_id": ObjectId(),
                "user_id": user_id,
                "dietary_restrictions": [],
                "cuisines": [],
                "calorie_goal": None,
                "address": None,
                "allergies": [],
                "favorite_meals": [meal['_id']]
            }
            result = db.user_preferences.insert_one(new_prefs)
            print(f"Created new preferences with ID: {result.inserted_id}")
        else:
            # Update existing preferences
            result = db.user_preferences.update_one(
                {"_id": user_prefs["_id"]},
                {"$addToSet": {"favorite_meals": meal['_id']}}
            )
            print(f"Updated user preferences: {result.modified_count} documents modified")
    else:
        print("No meals found in database")

print("\nDone!")
