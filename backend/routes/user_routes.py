from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.user_preferences import UserPreferences
from bson import ObjectId
from db import mongo
import datetime

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Check if required fields are present
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    # Check if user already exists
    existing_user = mongo.db.users.find_one({"email": data['email']})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
    # Create new user
    new_user = User(
        email=data['email'],
        password=data['password'],
        name=data.get('name')
    )
    
    # Insert user into database
    user_id = mongo.db.users.insert_one(new_user.to_dict()).inserted_id
    
    # Create default user preferences
    user_prefs = UserPreferences(user_id=user_id)
    mongo.db.user_preferences.insert_one(user_prefs.to_dict())
    
    # Set session
    session['user_id'] = str(user_id)
    
    return jsonify({
        "message": "User registered successfully",
        "user_id": str(user_id)
    }), 201

@user_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    
    # Check if required fields are present
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    # Find user by email
    user_dict = mongo.db.users.find_one({"email": data['email']})
    if not user_dict:
        print(f"User not found with email: {data['email']}")
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Check if user has password_hash field
    if 'password_hash' not in user_dict:
        print(f"User {data['email']} has no password_hash field")
        # If using password field directly
        if 'password' in user_dict and check_password_hash(user_dict['password'], data['password']):
            # Set session
            session['user_id'] = str(user_dict['_id'])
            
            # Update last login time
            mongo.db.users.update_one(
                {"_id": user_dict['_id']},
                {"$set": {"last_login": datetime.datetime.now()}}
            )
            
            return jsonify({
                "message": "Login successful",
                "user_id": str(user_dict['_id']),
                "name": user_dict.get('name'),
                "is_admin": user_dict.get('is_admin', False)
            }), 200
        else:
            print(f"Password mismatch for user: {data['email']}")
            return jsonify({"error": "Invalid email or password"}), 401
    
    # Create user object
    user = User.from_dict(user_dict)
    
    # Check password
    if not user.check_password(data['password']):
        print(f"Password mismatch for user: {data['email']}")
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Update last login time
    user.update_last_login()
    mongo.db.users.update_one(
        {"_id": user.user_id},
        {"$set": {"last_login": user.last_login}}
    )
    
    # Set session
    session['user_id'] = str(user.user_id)
    print(f"User logged in successfully: {user.email} with session ID: {session['user_id']}")
    
    return jsonify({
        "message": "Login successful",
        "user_id": str(user.user_id),
        "name": user.name,
        "is_admin": user.is_admin
    }), 200

@user_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a user"""
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"}), 200

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    
    # Get user from database
    user_dict = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        return jsonify({"error": "User not found"}), 404
    
    user = User.from_dict(user_dict)
    
    # Get user preferences
    prefs_dict = mongo.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
    
    # Process preferences to ensure ObjectId is converted to string
    if prefs_dict:
        # Convert all ObjectId values in preferences to strings
        for key, value in prefs_dict.items():
            if isinstance(value, ObjectId):
                prefs_dict[key] = str(value)
            elif isinstance(value, list):
                # Handle lists that might contain ObjectId values
                for i, item in enumerate(value):
                    if isinstance(item, ObjectId):
                        value[i] = str(item)
    
    # Create response
    response = {
        "user_id": str(user.user_id),
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "is_admin": user.is_admin,
        "preferences": prefs_dict if prefs_dict else {}
    }
    
    # Remove sensitive fields
    if "password_hash" in response:
        del response["password_hash"]
    
    return jsonify(response), 200

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    # Get user from database
    user_dict = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        return jsonify({"error": "User not found"}), 404
    
    user = User.from_dict(user_dict)
    
    # Update user fields
    if data.get('name'):
        user.name = data['name']
    
    # Update password if provided
    if data.get('password'):
        user.password_hash = generate_password_hash(data['password'])
    
    # Update user in database
    mongo.db.users.update_one(
        {"_id": user.user_id},
        {"$set": user.to_dict()}
    )
    
    return jsonify({"message": "Profile updated successfully"}), 200

@user_bp.route('/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    
    # Get user preferences from database
    prefs_dict = mongo.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
    if not prefs_dict:
        return jsonify({"error": "Preferences not found"}), 404
    
    # Convert all ObjectId values to strings for JSON serialization
    for key, value in prefs_dict.items():
        if isinstance(value, ObjectId):
            prefs_dict[key] = str(value)
        elif isinstance(value, list):
            # Handle lists that might contain ObjectId values (like favorite_meals)
            for i, item in enumerate(value):
                if isinstance(item, ObjectId):
                    value[i] = str(item)
    
    return jsonify(prefs_dict), 200

@user_bp.route('/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    # Get user preferences from database
    prefs_dict = mongo.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
    
    if not prefs_dict:
        # Create new preferences if not found
        prefs = UserPreferences(user_id=ObjectId(user_id))
        prefs_dict = prefs.to_dict()
    
    # Update preferences fields
    if data.get('dietary_restrictions') is not None:
        prefs_dict['dietary_restrictions'] = data['dietary_restrictions']
    
    if data.get('cuisines') is not None:
        prefs_dict['cuisines'] = data['cuisines']
    
    if data.get('calorie_goal') is not None:
        prefs_dict['calorie_goal'] = data['calorie_goal']
    
    if data.get('address') is not None:
        prefs_dict['address'] = data['address']
    
    if data.get('allergies') is not None:
        prefs_dict['allergies'] = data['allergies']
    
    # Update or insert preferences in database
    mongo.db.user_preferences.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": prefs_dict},
        upsert=True
    )
    
    return jsonify({"message": "Preferences updated successfully"}), 200

@user_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """Get user's favorite meals"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            print("User not logged in - unauthorized")
            return jsonify({"error": "Unauthorized"}), 401
        
        user_id = session['user_id']
        print(f"Getting favorites for user ID: {user_id}")
        
        # Get user preferences directly
        try:
            user_prefs = mongo.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
        except Exception as e:
            print(f"Error converting user_id to ObjectId: {str(e)}")
            # Try without conversion
            user_prefs = mongo.db.user_preferences.find_one({"user_id": user_id})
        
        # If user has no preferences yet, return empty array
        if not user_prefs:
            print(f"User {user_id} has no preferences yet")
            return jsonify([]), 200
        
        print(f"User preferences found with ID: {user_prefs.get('_id')}")
        
        # Get favorite meals
        favorite_meals = []
        for meal_id in user_prefs.get('favorite_meals', []):
            try:
                print(f"Processing favorite meal ID: {meal_id}")
                if isinstance(meal_id, str):
                    meal_id = ObjectId(meal_id)
                
                meal_dict = mongo.db.meals.find_one({"_id": meal_id})
                if meal_dict:
                    print(f"Found meal: {meal_dict.get('name')}")
                    # Convert to serializable format
                    serialized_meal = {
                        "_id": str(meal_dict["_id"]),
                        "name": meal_dict.get("name", ""),
                        "description": meal_dict.get("description", ""),
                        "image_url": meal_dict.get("image_url", ""),
                        "prep_time": meal_dict.get("prep_time", 0),
                        "cook_time": meal_dict.get("cook_time", 0),
                        "servings": meal_dict.get("servings", 0),
                        "difficulty": meal_dict.get("difficulty", ""),
                        "cuisine_type": meal_dict.get("cuisine_type", ""),
                        "meal_type": meal_dict.get("meal_type", ""),
                        "ingredients": meal_dict.get("ingredients", []),
                        "instructions": meal_dict.get("instructions", []),
                        "mood_tags": meal_dict.get("mood_tags", []),
                        "rating": meal_dict.get("rating", 0),
                        "review_count": meal_dict.get("review_count", 0)
                    }
                    
                    # Handle nutritional_info if present
                    if "nutritional_info" in meal_dict:
                        nutritional_info = meal_dict["nutritional_info"]
                        serialized_meal["nutritional_info"] = {
                            "calories": nutritional_info.get("calories", 0),
                            "protein": nutritional_info.get("protein", 0),
                            "carbs": nutritional_info.get("carbs", 0),
                            "fat": nutritional_info.get("fat", 0),
                            "sugar": nutritional_info.get("sugar", 0),
                            "fiber": nutritional_info.get("fiber", 0),
                            "dietary_tags": nutritional_info.get("dietary_tags", [])
                        }
                    
                    favorite_meals.append(serialized_meal)
                else:
                    print(f"Meal not found for ID: {meal_id}")
            except Exception as e:
                print(f"Error processing meal {meal_id}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"Found {len(favorite_meals)} favorite meals for user {user_id}")
        return jsonify(favorite_meals), 200
    except Exception as e:
        print(f"Unexpected error in get_favorites: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/favorites/<meal_id>', methods=['POST'])
def add_favorite(meal_id):
    """Add a meal to favorites"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            print("User not logged in - unauthorized")
            return jsonify({"error": "Unauthorized"}), 401
        
        user_id = session['user_id']
        print(f"Adding favorite meal {meal_id} for user {user_id}")
        
        # Check if meal exists
        try:
            meal = mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
            if not meal:
                print(f"Meal not found: {meal_id}")
                return jsonify({"error": "Meal not found"}), 404
            
            print(f"Found meal: {meal.get('name')}")
        except Exception as e:
            print(f"Error finding meal: {str(e)}")
            return jsonify({"error": f"Invalid meal ID: {str(e)}"}), 400
        
        # Check if user preferences exist, if not create them
        try:
            # Try both with and without ObjectId conversion
            user_prefs = mongo.db.user_preferences.find_one({"user_id": ObjectId(user_id)})
            if not user_prefs:
                # Try without conversion
                user_prefs = mongo.db.user_preferences.find_one({"user_id": user_id})
            
            if not user_prefs:
                print(f"Creating new user preferences for user {user_id}")
                # Create new user preferences
                new_prefs = {
                    "_id": ObjectId(),
                    "user_id": ObjectId(user_id),
                    "dietary_restrictions": [],
                    "cuisines": [],
                    "calorie_goal": None,
                    "address": None,
                    "allergies": [],
                    "favorite_meals": [ObjectId(meal_id)]
                }
                result = mongo.db.user_preferences.insert_one(new_prefs)
                print(f"Created new preferences with ID: {result.inserted_id}")
                return jsonify({"message": "Meal added to favorites"}), 200
            
            # Update user preferences
            print(f"Updating existing preferences for user {user_id}")
            result = mongo.db.user_preferences.update_one(
                {"_id": user_prefs["_id"]},
                {"$addToSet": {"favorite_meals": ObjectId(meal_id)}}
            )
            
            print(f"Updated user preferences: {result.modified_count} documents modified")
            
            # Verify the update worked
            updated_prefs = mongo.db.user_preferences.find_one({"_id": user_prefs["_id"]})
            print(f"Updated preferences: {updated_prefs}")
            
            return jsonify({"message": "Meal added to favorites"}), 200
        except Exception as e:
            print(f"Error updating preferences: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to add favorite: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error in add_favorite: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/favorites/<meal_id>', methods=['DELETE'])
def remove_favorite(meal_id):
    """Remove a meal from favorites"""
    # Check if user is logged in
    if 'user_id' not in session:
        print("User not logged in - unauthorized")
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    print(f"Removing favorite meal {meal_id} for user {user_id}")
    
    # Update user preferences
    try:
        result = mongo.db.user_preferences.update_one(
            {"user_id": ObjectId(user_id)},
            {"$pull": {"favorite_meals": ObjectId(meal_id)}}
        )
        print(f"Updated user preferences: {result.modified_count} documents modified")
    except Exception as e:
        print(f"Error updating preferences: {str(e)}")
        return jsonify({"error": f"Failed to remove favorite: {str(e)}"}), 500
    
    return jsonify({"message": "Meal removed from favorites"}), 200

@user_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check current user session"""
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            print(f"User is logged in with ID: {user_id}")
            
            # Get user info
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                # Remove sensitive info
                if 'password' in user:
                    del user['password']
                
                # Convert ObjectId to string
                user['_id'] = str(user['_id'])
                
                return jsonify({
                    "authenticated": True,
                    "user_id": user_id,
                    "user": user
                }), 200
            else:
                print(f"User ID {user_id} in session but not found in database")
                return jsonify({
                    "authenticated": False,
                    "error": "User not found in database"
                }), 401
        else:
            print("No user_id in session")
            return jsonify({
                "authenticated": False,
                "error": "Not authenticated"
            }), 401
    except Exception as e:
        print(f"Error checking session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "authenticated": False,
            "error": f"Error checking session: {str(e)}"
        }), 500
