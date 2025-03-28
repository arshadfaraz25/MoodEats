import json
import os
import sys
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from bson import ObjectId

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models.user import User
from backend.models.mood_log import MoodLog

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

def clear_collections():
    """Clear all collections in the database"""
    print("Clearing existing collections...")
    db.users.delete_many({})
    db.meals.delete_many({})
    db.mood_logs.delete_many({})
    print("Collections cleared.")

def load_sample_meals():
    """Load sample meals from JSON file"""
    print("Loading sample meals...")
    
    # Read meals from JSON file
    with open('sample_meals.json', 'r') as file:
        meals = json.load(file)
    
    # Insert meals into database
    for meal in meals:
        # Add creation timestamp
        meal['created_at'] = datetime.now()
        meal['updated_at'] = datetime.now()
        
        # Add empty feedback array
        meal['feedback'] = []
        
        # Insert meal
        db.meals.insert_one(meal)
    
    print(f"Loaded {len(meals)} sample meals.")

def create_sample_users():
    """Create sample users"""
    print("Creating sample users...")
    
    # Create admin user
    admin_user = User(
        email="admin@moodeats.com",
        password="adminpassword",
        name="Admin User",
        is_admin=True
    )
    db.users.insert_one(admin_user.to_dict())
    
    # Create regular users
    users = [
        {
            "email": "john@example.com",
            "password": "password123",
            "name": "John Doe",
            "preferences": {
                "dietary_restrictions": ["Vegetarian"],
                "allergies": ["Nuts"],
                "favorite_cuisines": ["Italian", "Mexican"]
            }
        },
        {
            "email": "jane@example.com",
            "password": "password123",
            "name": "Jane Smith",
            "preferences": {
                "dietary_restrictions": ["Vegan"],
                "allergies": [],
                "favorite_cuisines": ["Thai", "Indian"]
            }
        },
        {
            "email": "bob@example.com",
            "password": "password123",
            "name": "Bob Johnson",
            "preferences": {
                "dietary_restrictions": ["Gluten-Free"],
                "allergies": ["Dairy"],
                "favorite_cuisines": ["American", "Mediterranean"]
            }
        }
    ]
    
    user_ids = []
    for user_data in users:
        user = User(
            email=user_data["email"],
            password=user_data["password"],
            name=user_data["name"],
            preferences=user_data["preferences"]
        )
        result = db.users.insert_one(user.to_dict())
        user_ids.append(result.inserted_id)
    
    print(f"Created {len(users) + 1} sample users.")
    return user_ids

def create_sample_mood_logs(user_ids):
    """Create sample mood logs for users"""
    print("Creating sample mood logs...")
    
    # Available moods
    moods = ["happy", "sad", "stressed", "relaxed", "energetic", "tired", "hungry", "bored", "sick", "celebratory"]
    
    # Sample notes
    notes = [
        "Feeling great today!",
        "Had a productive day at work",
        "Stressed about upcoming deadline",
        "Relaxing after a long day",
        "Need some comfort food",
        "Celebrating a promotion",
        "Not feeling well today",
        "Looking for something exciting",
        "Just finished a workout",
        "Need energy boost",
        None  # Some entries without notes
    ]
    
    # Create mood logs for each user
    total_logs = 0
    for user_id in user_ids:
        # Create 5-10 mood logs per user
        num_logs = random.randint(5, 10)
        
        for i in range(num_logs):
            # Random date within the last 30 days
            days_ago = random.randint(0, 30)
            timestamp = datetime.now() - timedelta(days=days_ago, 
                                                 hours=random.randint(0, 23),
                                                 minutes=random.randint(0, 59))
            
            # Create mood log
            mood_log = MoodLog(
                user_id=user_id,
                mood=random.choice(moods),
                notes=random.choice(notes),
                timestamp=timestamp
            )
            
            # Insert mood log
            db.mood_logs.insert_one(mood_log.to_dict())
            total_logs += 1
    
    print(f"Created {total_logs} sample mood logs.")

def create_user_favorites(user_ids):
    """Add favorite meals for users"""
    print("Adding favorite meals for users...")
    
    # Get all meal IDs
    meal_ids = [meal["_id"] for meal in db.meals.find({}, {"_id": 1})]
    
    # Add favorites for each user
    for user_id in user_ids:
        # Select 2-5 random meals as favorites
        num_favorites = random.randint(2, 5)
        favorite_meals = random.sample(meal_ids, num_favorites)
        
        # Update user with favorites
        db.users.update_one(
            {"_id": user_id},
            {"$set": {"favorite_meals": favorite_meals}}
        )
    
    print(f"Added favorites for {len(user_ids)} users.")

def main():
    """Main function to load all sample data"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting to load sample data...")
    
    # Clear existing data
    clear_collections()
    
    # Load data
    load_sample_meals()
    user_ids = create_sample_users()
    create_sample_mood_logs(user_ids)
    create_user_favorites(user_ids)
    
    print("Sample data loaded successfully!")
    print("\nSample user credentials:")
    print("Admin: admin@moodeats.com / adminpassword")
    print("User 1: john@example.com / password123")
    print("User 2: jane@example.com / password123")
    print("User 3: bob@example.com / password123")

if __name__ == "__main__":
    main()
