# Python Control Structures in MoodEats Backend

This document provides real examples of Python control structures used in the MoodEats backend codebase.

## If Statements

```python
# Basic authentication check from user_routes.py
@user_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check current user session"""
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            
            # Get user info
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                # Remove sensitive info
                if 'password' in user:
                    del user['password']
                
                return jsonify({
                    "authenticated": True,
                    "user": user
                })
            else:
                return jsonify({
                    "authenticated": False,
                    "error": "User not found in database"
                }), 401
        else:
            return jsonify({
                "authenticated": False,
                "error": "Not authenticated"
            }), 401
    except Exception as e:
        return jsonify({
            "authenticated": False,
            "error": f"Error checking session: {str(e)}"
        }), 500
```

## For Loops

```python
# Processing meals in get_favorites from user_routes.py
for meal_id in favorite_meal_ids:
    try:
        meal = mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
        if meal:
            # Convert ObjectId to string for JSON serialization
            meal["_id"] = str(meal["_id"])
            favorite_meals.append(meal)
        else:
            print(f"Meal not found for ID: {meal_id}")
    except Exception as e:
        print(f"Error processing meal {meal_id}: {str(e)}")
```

## Try/Except Blocks

```python
# Error handling in add_favorite from user_routes.py
@user_bp.route('/favorites/<meal_id>', methods=['POST'])
def add_favorite(meal_id):
    """Add a meal to favorites"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        
        user_id = session['user_id']
        
        # Check if meal exists
        try:
            meal = mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
            if not meal:
                return jsonify({"error": "Meal not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Invalid meal ID: {str(e)}"}), 400
        
        # Update user preferences
        try:
            result = mongo.db.user_preferences.update_one(
                {"user_id": ObjectId(user_id)},
                {"$addToSet": {"favorite_meals": ObjectId(meal_id)}}
            )
            return jsonify({"message": "Meal added to favorites"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to add favorite: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500
```

## List Comprehensions

```python
# Converting feedback dictionaries to objects in database_manager.py
def get_meal_feedback(self, meal_id, limit=10):
    """Get feedback for a specific meal"""
    feedback_dicts = self.db.feedback.find(
        {"meal_id": ObjectId(meal_id)}
    ).sort("timestamp", -1).limit(limit)
    
    return [Feedback.from_dict(f_dict) for f_dict in feedback_dicts]
```

## Conditional Expressions (Ternary Operator)

```python
# Default value handling in User.__init__
def __init__(self, email, password=None, name=None, user_id=None, created_at=None, 
             last_login=None, is_admin=False, preferences=None, password_hash=None):
    self.user_id = user_id if user_id else ObjectId()
    self.email = email
    self.password_hash = password_hash if password_hash else (generate_password_hash(password) if password else None)
    self.name = name
    self.created_at = created_at if created_at else datetime.now()
    self.last_login = last_login
    self.is_admin = is_admin
    self.preferences = preferences if preferences else {}
```

## Type Checking

```python
# Type checking in MongoJSONEncoder.default
def default(self, obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    return super().default(obj)
```

## Function Decorators

```python
# Admin authentication decorator in admin_routes.py
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        
        user_id = session['user_id']
        
        # Check if user is an admin
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user or not user.get('is_admin', False):
            return jsonify({"error": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
```

## Switch-like Pattern with Dictionary Mapping

```python
# Mood to food characteristics mapping in RecommendationEngine
self.mood_food_mapping = {
    "happy": ["comfort food", "celebratory", "colorful", "sweet"],
    "sad": ["comfort food", "warm", "nostalgic", "chocolate"],
    "stressed": ["calming", "easy to prepare", "nutrient-rich", "soothing"],
    "energetic": ["protein-rich", "complex carbs", "fresh", "vibrant"],
    "tired": ["energy-boosting", "iron-rich", "protein", "simple"],
    "anxious": ["calming", "soothing", "warm", "simple"],
    "nostalgic": ["traditional", "comfort food", "homestyle", "familiar"],
    "relaxed": ["light", "refreshing", "balanced", "simple"]
}

# Usage:
food_characteristics = self.mood_food_mapping.get(mood.lower(), [])
```

## Key Python Control Flow Patterns in MoodEats

1. **Authentication Checks**: Consistent pattern of checking session status before allowing access to protected routes

2. **Error Handling**: Nested try/except blocks with specific error messages and status codes

3. **Default Value Handling**: Using the `value if condition else default` pattern for initialization

4. **List Comprehensions**: Used for concise data transformation, especially when converting between database and model objects

5. **Decorators**: Used for cross-cutting concerns like authentication and authorization

6. **Dictionary Mappings**: Used as alternatives to switch statements for mapping between related values

7. **Early Returns**: Functions often return early for validation errors to reduce nesting and improve readability
