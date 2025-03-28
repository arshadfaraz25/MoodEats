from pymongo import MongoClient
from bson import ObjectId
import json

# Custom JSON encoder to handle ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

# User ID to update
user_id_str = "67e5b44627a9382198557540"
user_id = ObjectId(user_id_str)

# Meal ID to add as favorite
meal_id_str = "67e5af4a4344fe1865108e1b"  # Chocolate Chip Banana Pancakes
meal_id = ObjectId(meal_id_str)

# Check if user exists
user = db.users.find_one({"_id": user_id})
if not user:
    print(f"User with ID {user_id_str} not found!")
    exit(1)

print(f"Found user: {user.get('email')}")

# Check if user preferences exist
user_prefs = db.user_preferences.find_one({"user_id": user_id})

if not user_prefs:
    print(f"Creating new preferences for user {user_id_str}")
    # Create new user preferences
    new_prefs = {
        "_id": ObjectId(),
        "user_id": user_id,
        "dietary_restrictions": [],
        "cuisines": [],
        "calorie_goal": None,
        "address": None,
        "allergies": [],
        "favorite_meals": [meal_id]
    }
    result = db.user_preferences.insert_one(new_prefs)
    print(f"Created new preferences with ID: {result.inserted_id}")
    user_prefs = db.user_preferences.find_one({"_id": result.inserted_id})
else:
    print(f"Updating existing preferences for user {user_id_str}")
    # Add meal to favorites
    result = db.user_preferences.update_one(
        {"_id": user_prefs["_id"]},
        {"$addToSet": {"favorite_meals": meal_id}}
    )
    print(f"Updated user preferences: {result.modified_count} documents modified")
    user_prefs = db.user_preferences.find_one({"_id": user_prefs["_id"]})

# Print updated preferences
print("\nUpdated preferences:")
print(json.dumps(user_prefs, cls=MongoJSONEncoder, indent=2))

# Check if meal exists
meal = db.meals.find_one({"_id": meal_id})
if meal:
    print(f"\nAdded meal: {meal.get('name')}")
else:
    print(f"\nMeal with ID {meal_id_str} not found!")

# Get all favorite meals
favorite_meals = []
for fav_meal_id in user_prefs.get('favorite_meals', []):
    meal = db.meals.find_one({"_id": fav_meal_id})
    if meal:
        favorite_meals.append({
            "id": str(meal["_id"]),
            "name": meal.get("name")
        })

print("\nAll favorite meals:")
print(json.dumps(favorite_meals, indent=2))
