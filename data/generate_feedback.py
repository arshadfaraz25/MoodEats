import os
import sys
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

def generate_sample_feedback():
    """Generate sample feedback for meals"""
    print("Generating sample feedback for meals...")
    
    # Get all meal IDs
    meals = list(db.meals.find({}, {"_id": 1, "name": 1}))
    
    # Get all user IDs
    users = list(db.users.find({}, {"_id": 1, "name": 1}))
    
    if not meals or not users:
        print("Error: No meals or users found in the database.")
        return
    
    # Sample feedback comments
    positive_comments = [
        "Loved this recipe! It was exactly what I needed for my mood.",
        "Perfect balance of flavors. Will definitely make again!",
        "This was so easy to make and tasted amazing.",
        "Great recipe! The whole family enjoyed it.",
        "This really helped improve my mood. Thank you!",
        "Delicious and satisfying. Perfect comfort food.",
        "I was skeptical at first, but this was fantastic!",
        "The flavors worked so well together. Yum!",
        "This has become one of my favorite recipes.",
        "Simple to make but tastes gourmet!"
    ]
    
    neutral_comments = [
        "It was okay, but I might adjust the seasoning next time.",
        "Decent recipe, but not my favorite.",
        "Good but not great. Might try again with some modifications.",
        "It was fine for a quick meal.",
        "Not bad, but I've had better."
    ]
    
    negative_comments = [
        "This didn't really match my mood as expected.",
        "Too complicated for the end result.",
        "The flavors didn't work for me.",
        "I expected more based on the description.",
        "Not my cup of tea, unfortunately."
    ]
    
    # Generate feedback
    total_feedback = 0
    
    for meal in meals:
        # Determine number of feedback entries for this meal (0-5)
        num_feedback = random.randint(0, 5)
        
        # Skip if no feedback
        if num_feedback == 0:
            continue
        
        # Get random users for this meal
        meal_users = random.sample(users, min(num_feedback, len(users)))
        
        feedback_list = []
        
        for user in meal_users:
            # Random date within the last 60 days
            days_ago = random.randint(0, 60)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            # Random rating (1-5)
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30], k=1)[0]
            
            # Select comment based on rating
            if rating >= 4:
                comment = random.choice(positive_comments)
            elif rating == 3:
                comment = random.choice(neutral_comments)
            else:
                comment = random.choice(negative_comments)
            
            # Create feedback object
            feedback = {
                "user_id": user["_id"],
                "user_name": user.get("name", "Anonymous"),
                "rating": rating,
                "comment": comment,
                "timestamp": timestamp
            }
            
            feedback_list.append(feedback)
            total_feedback += 1
        
        # Update meal with feedback
        db.meals.update_one(
            {"_id": meal["_id"]},
            {"$set": {"feedback": feedback_list}}
        )
        
        # Calculate and update average rating
        if feedback_list:
            avg_rating = sum(f["rating"] for f in feedback_list) / len(feedback_list)
            db.meals.update_one(
                {"_id": meal["_id"]},
                {"$set": {"average_rating": round(avg_rating, 1)}}
            )
    
    print(f"Generated {total_feedback} feedback entries across {len(meals)} meals.")

def main():
    """Main function to generate sample feedback"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting to generate sample feedback...")
    generate_sample_feedback()
    print("Sample feedback generated successfully!")

if __name__ == "__main__":
    main()
