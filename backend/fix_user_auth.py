from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash
import json
import datetime

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

# User ID to fix
user_id_str = "67e5b44627a9382198557540"
user_id = ObjectId(user_id_str)

# Check if user exists
user = db.users.find_one({"_id": user_id})
if user:
    print(f"Found user: {user.get('email')}")
    
    # Check if user has password_hash field
    if 'password_hash' in user:
        print(f"User has password_hash field: {user['password_hash'][:20]}...")
    else:
        print("User does not have password_hash field")
    
    # Generate new password hash
    new_password = "password123"
    password_hash = generate_password_hash(new_password)
    
    # Update user with password_hash field
    result = db.users.update_one(
        {"_id": user_id},
        {"$set": {"password_hash": password_hash}}
    )
    
    print(f"Password updated: {result.modified_count} document modified")
    print(f"New password: {new_password}")
    print(f"New password hash: {password_hash}")
    
    # Verify update
    updated_user = db.users.find_one({"_id": user_id})
    if 'password_hash' in updated_user:
        print(f"Verified: User now has password_hash field: {updated_user['password_hash'][:20]}...")
    else:
        print("ERROR: User still does not have password_hash field")
else:
    print(f"User with ID {user_id_str} not found!")

print("\nDone!")
