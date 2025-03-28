from pymongo import MongoClient
from bson import ObjectId
import json
import datetime
from werkzeug.security import generate_password_hash

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

# List all users
print("All users in the database:")
users = list(db.users.find())
for user in users:
    # Remove password from output
    if 'password' in user:
        user['password'] = '***HIDDEN***'
    print(json.dumps(user, cls=MongoJSONEncoder, indent=2))

# Reset password for test user
user_id_str = "67e5b44627a9382198557540"
user_id = ObjectId(user_id_str)

# Check if user exists
user = db.users.find_one({"_id": user_id})
if user:
    print(f"\nResetting password for user: {user.get('email')}")
    
    # Generate new password hash
    new_password = "password123"
    password_hash = generate_password_hash(new_password)
    
    # Update user
    result = db.users.update_one(
        {"_id": user_id},
        {"$set": {"password": password_hash}}
    )
    
    print(f"Password reset: {result.modified_count} document modified")
    print(f"New password: {new_password}")
else:
    print(f"\nUser with ID {user_id_str} not found!")

print("\nDone!")
