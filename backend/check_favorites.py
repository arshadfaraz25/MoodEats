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

# Get users
print("Users:")
users = list(db.users.find())
for user in users:
    print(f"User ID: {user['_id']}, Email: {user.get('email')}")

# Get user preferences
print("\nUser Preferences:")
prefs = list(db.user_preferences.find())
for pref in prefs:
    print(json.dumps(pref, cls=MongoJSONEncoder, indent=2))
    
    # Check if this user has favorite meals
    if 'favorite_meals' in pref and pref['favorite_meals']:
        print(f"\nFavorite meals for user {pref['user_id']}:")
        for meal_id in pref['favorite_meals']:
            meal = db.meals.find_one({"_id": meal_id})
            if meal:
                print(f"  - {meal.get('name')} (ID: {meal_id})")
            else:
                print(f"  - Meal not found (ID: {meal_id})")
    else:
        print(f"\nNo favorite meals for user {pref['user_id']}")

# Check session collection
print("\nSessions:")
sessions = list(db.sessions.find()) if 'sessions' in db.list_collection_names() else []
print(f"Total sessions: {len(sessions)}")
for session in sessions:
    print(json.dumps(session, cls=MongoJSONEncoder, indent=2))
