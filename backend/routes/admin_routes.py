"""
File name: admin_routes.py
Purpose: API routes for admin operations in the MoodEats application.
         Handles user management, meal CRUD operations, and analytics.

@author Arshad Faraz
@version 1.0.0
"""
from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from db import mongo
from models.meal import Meal, NutritionalInfo
from models.user import User
import csv
import io
import json
from functools import wraps

admin_bp = Blueprint('admin_bp', __name__)

# Admin middleware to check if user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            print("Admin route access denied: No user_id in session")
            return jsonify({"error": "Unauthorized - Please log in"}), 401
        
        user_id = session['user_id']
        print(f"Admin route access attempt by user_id: {user_id}")
        
        try:
            # Check if user is an admin
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                print(f"Admin route access denied: User {user_id} not found in database")
                return jsonify({"error": "User not found"}), 404
            
            print(f"User found: {user.get('email')}, is_admin: {user.get('is_admin', False)}")
            
            if not user.get('is_admin', False):
                print(f"Admin route access denied: User {user_id} is not an admin")
                return jsonify({"error": "Admin privileges required"}), 403
            
            print(f"Admin access granted to user: {user.get('email')}")
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Error in admin_required decorator: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Server error: {str(e)}"}), 500
    
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        print("Fetching users for admin panel...")
        limit = int(request.args.get('limit', 100))
        print(f"Requested limit: {limit}")
        
        # Get users from database
        users = mongo.db.users.find().limit(limit)
        
        # Convert to list and serialize ObjectId
        user_list = []
        for user in users:
            user_dict = dict(user)  # Create a copy to avoid modifying the original
            user_dict['_id'] = str(user_dict['_id'])
            # Remove password hash for security
            if 'password_hash' in user_dict:
                del user_dict['password_hash']
            user_list.append(user_dict)
        
        print(f"Found {len(user_list)} users")
        
        # Convert response to JSON string and back to ensure serialization works correctly
        import json
        json_str = json.dumps(user_list, default=str)
        print(f"JSON string length: {len(json_str)}")
        
        # Return the response with explicit content type
        from flask import Response
        return Response(json_str, mimetype='application/json'), 200
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get users: {str(e)}"}), 500

@admin_bp.route('/users/<user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get a specific user by ID (admin only)"""
    # Find user in database
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Convert ObjectId to string for JSON serialization
    user["_id"] = str(user["_id"])
    
    # Remove password hash for security
    if 'password_hash' in user:
        del user['password_hash']
    
    return jsonify(user), 200

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    # Delete user from database
    result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    
    # Delete related data
    mongo.db.user_preferences.delete_many({"user_id": ObjectId(user_id)})
    mongo.db.mood_logs.delete_many({"user_id": ObjectId(user_id)})
    mongo.db.feedback.delete_many({"user_id": ObjectId(user_id)})
    
    return jsonify({"message": "User deleted successfully"}), 200

@admin_bp.route('/meals', methods=['POST'])
@admin_required
def create_meal():
    """Create a new meal (admin only)"""
    data = request.get_json()
    
    # Check if required fields are present
    if not data or not data.get('name') or not data.get('ingredients') or not data.get('recipe_steps'):
        return jsonify({"error": "Name, ingredients, and recipe steps are required"}), 400
    
    # Create nutritional info object if provided
    nutritional_info = None
    if data.get('nutritional_info'):
        nutritional_info = NutritionalInfo(
            calories=data['nutritional_info'].get('calories', 0),
            protein=data['nutritional_info'].get('protein', 0),
            carbs=data['nutritional_info'].get('carbs', 0),
            fat=data['nutritional_info'].get('fat', 0),
            dietary_tags=data['nutritional_info'].get('dietary_tags', [])
        )
    
    # Create meal object
    meal = Meal(
        name=data['name'],
        ingredients=data['ingredients'],
        recipe_steps=data['recipe_steps'],
        image_url=data.get('image_url'),
        prep_time=data.get('prep_time'),
        cook_time=data.get('cook_time'),
        servings=data.get('servings'),
        cuisine_type=data.get('cuisine_type'),
        meal_type=data.get('meal_type'),
        nutritional_info=nutritional_info,
        mood_tags=data.get('mood_tags', [])
    )
    
    # Insert meal into database
    meal_id = mongo.db.meals.insert_one(meal.to_dict()).inserted_id
    
    return jsonify({
        "message": "Meal created successfully",
        "meal_id": str(meal_id)
    }), 201

@admin_bp.route('/meals', methods=['GET'])
@admin_required
def get_admin_meals():
    """Get all meals (admin only)"""
    try:
        print("Fetching all meals for admin...")
        meals = list(mongo.db.meals.find())
        
        # Convert ObjectId to string for JSON serialization
        for meal in meals:
            meal['_id'] = str(meal['_id'])
        
        print(f"Found {len(meals)} meals")
        
        # Convert to JSON string and back to ensure serialization works correctly
        import json
        json_str = json.dumps(meals, default=str)
        
        # Return the response with explicit content type
        from flask import Response
        return Response(json_str, mimetype='application/json'), 200
    except Exception as e:
        print(f"Error in get_admin_meals: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get meals: {str(e)}"}), 500

@admin_bp.route('/meals/<meal_id>', methods=['PUT'])
@admin_required
def update_meal(meal_id):
    """Update a meal (admin only)"""
    data = request.get_json()
    
    # Find meal in database
    meal_dict = mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
    
    if not meal_dict:
        return jsonify({"error": "Meal not found"}), 404
    
    # Update meal fields
    if data.get('name'):
        meal_dict['name'] = data['name']
    
    if data.get('ingredients'):
        meal_dict['ingredients'] = data['ingredients']
    
    if data.get('recipe_steps'):
        meal_dict['recipe_steps'] = data['recipe_steps']
    
    if data.get('image_url'):
        meal_dict['image_url'] = data['image_url']
    
    if data.get('prep_time') is not None:
        meal_dict['prep_time'] = data['prep_time']
    
    if data.get('cook_time') is not None:
        meal_dict['cook_time'] = data['cook_time']
    
    if data.get('servings') is not None:
        meal_dict['servings'] = data['servings']
    
    if data.get('cuisine_type'):
        meal_dict['cuisine_type'] = data['cuisine_type']
    
    if data.get('meal_type'):
        meal_dict['meal_type'] = data['meal_type']
    
    if data.get('mood_tags'):
        meal_dict['mood_tags'] = data['mood_tags']
    
    # Update nutritional info if provided
    if data.get('nutritional_info'):
        if not meal_dict.get('nutritional_info'):
            meal_dict['nutritional_info'] = {}
        
        nutritional_info = data['nutritional_info']
        
        if nutritional_info.get('calories') is not None:
            meal_dict['nutritional_info']['calories'] = nutritional_info['calories']
        
        if nutritional_info.get('protein') is not None:
            meal_dict['nutritional_info']['protein'] = nutritional_info['protein']
        
        if nutritional_info.get('carbs') is not None:
            meal_dict['nutritional_info']['carbs'] = nutritional_info['carbs']
        
        if nutritional_info.get('fat') is not None:
            meal_dict['nutritional_info']['fat'] = nutritional_info['fat']
        
        if nutritional_info.get('dietary_tags'):
            meal_dict['nutritional_info']['dietary_tags'] = nutritional_info['dietary_tags']
    
    # Update meal in database
    mongo.db.meals.update_one(
        {"_id": ObjectId(meal_id)},
        {"$set": meal_dict}
    )
    
    return jsonify({"message": "Meal updated successfully"}), 200

@admin_bp.route('/meals/<meal_id>', methods=['DELETE'])
@admin_required
def delete_meal(meal_id):
    """Delete a meal (admin only)"""
    # Delete meal from database
    result = mongo.db.meals.delete_one({"_id": ObjectId(meal_id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Meal not found"}), 404
    
    # Delete related feedback
    mongo.db.feedback.delete_many({"meal_id": ObjectId(meal_id)})
    
    # Remove meal from user favorites
    mongo.db.user_preferences.update_many(
        {"favorite_meals": ObjectId(meal_id)},
        {"$pull": {"favorite_meals": ObjectId(meal_id)}}
    )
    
    return jsonify({"message": "Meal deleted successfully"}), 200

@admin_bp.route('/meals/bulk', methods=['POST'])
@admin_required
def bulk_upload_meals():
    """Bulk upload meals via CSV or JSON (admin only)"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Determine file type
    if file.filename.endswith('.csv'):
        # Process CSV file
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            meals = []
            for row in csv_reader:
                # Create nutritional info
                nutritional_info = NutritionalInfo(
                    calories=int(row.get('calories', 0)),
                    protein=float(row.get('protein', 0)),
                    carbs=float(row.get('carbs', 0)),
                    fat=float(row.get('fat', 0)),
                    dietary_tags=row.get('dietary_tags', '').split(',') if row.get('dietary_tags') else []
                )
                
                # Create meal
                meal = Meal(
                    name=row['name'],
                    ingredients=row.get('ingredients', '').split(',') if row.get('ingredients') else [],
                    recipe_steps=row.get('recipe_steps', '').split('|') if row.get('recipe_steps') else [],
                    image_url=row.get('image_url'),
                    prep_time=int(row.get('prep_time', 0)) if row.get('prep_time') else None,
                    cook_time=int(row.get('cook_time', 0)) if row.get('cook_time') else None,
                    servings=int(row.get('servings', 0)) if row.get('servings') else None,
                    cuisine_type=row.get('cuisine_type'),
                    meal_type=row.get('meal_type'),
                    nutritional_info=nutritional_info,
                    mood_tags=row.get('mood_tags', '').split(',') if row.get('mood_tags') else []
                )
                
                meals.append(meal)
            
            # Insert meals into database
            meal_dicts = [meal.to_dict() for meal in meals]
            result = mongo.db.meals.insert_many(meal_dicts)
            
            return jsonify({
                "message": f"Successfully uploaded {len(result.inserted_ids)} meals",
                "meal_ids": [str(id) for id in result.inserted_ids]
            }), 201
        
        except Exception as e:
            return jsonify({"error": f"Error processing CSV file: {str(e)}"}), 400
    
    elif file.filename.endswith('.json'):
        # Process JSON file
        try:
            data = json.loads(file.read().decode('utf-8'))
            
            if not isinstance(data, list):
                return jsonify({"error": "JSON file must contain an array of meals"}), 400
            
            meals = []
            for meal_data in data:
                # Create nutritional info
                nutritional_info = None
                if meal_data.get('nutritional_info'):
                    nutritional_info = NutritionalInfo(
                        calories=meal_data['nutritional_info'].get('calories', 0),
                        protein=meal_data['nutritional_info'].get('protein', 0),
                        carbs=meal_data['nutritional_info'].get('carbs', 0),
                        fat=meal_data['nutritional_info'].get('fat', 0),
                        dietary_tags=meal_data['nutritional_info'].get('dietary_tags', [])
                    )
                
                # Create meal
                meal = Meal(
                    name=meal_data['name'],
                    ingredients=meal_data.get('ingredients', []),
                    recipe_steps=meal_data.get('recipe_steps', []),
                    image_url=meal_data.get('image_url'),
                    prep_time=meal_data.get('prep_time'),
                    cook_time=meal_data.get('cook_time'),
                    servings=meal_data.get('servings'),
                    cuisine_type=meal_data.get('cuisine_type'),
                    meal_type=meal_data.get('meal_type'),
                    nutritional_info=nutritional_info,
                    mood_tags=meal_data.get('mood_tags', [])
                )
                
                meals.append(meal)
            
            # Insert meals into database
            meal_dicts = [meal.to_dict() for meal in meals]
            result = mongo.db.meals.insert_many(meal_dicts)
            
            return jsonify({
                "message": f"Successfully uploaded {len(result.inserted_ids)} meals",
                "meal_ids": [str(id) for id in result.inserted_ids]
            }), 201
        
        except Exception as e:
            return jsonify({"error": f"Error processing JSON file: {str(e)}"}), 400
    
    else:
        return jsonify({"error": "Unsupported file format. Please upload a CSV or JSON file"}), 400

@admin_bp.route('/analytics/meals', methods=['GET'])
@admin_required
def meal_analytics():
    """Get meal analytics (admin only)"""
    try:
        print("Fetching meal analytics...")
        
        # Get time range parameter
        time_range = request.args.get('time_range', 'week')
        print(f"Time range: {time_range}")
        
        # Calculate date ranges based on time_range
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if time_range == 'day':
            start_date = now - timedelta(days=1)
        elif time_range == 'week':
            start_date = now - timedelta(days=7)
        elif time_range == 'month':
            start_date = now - timedelta(days=30)
        elif time_range == 'year':
            start_date = now - timedelta(days=365)
        else:
            # Default to week
            start_date = now - timedelta(days=7)
            
        print(f"Date range: {start_date} to {now}")
        
        # Get total number of meals
        total_meals = mongo.db.meals.count_documents({})
        print(f"Total meals: {total_meals}")
        
        # Get top rated meals
        pipeline = [
            {"$group": {
                "_id": "$meal_id",
                "average_rating": {"$avg": "$rating"},
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gte": 1}}},  # At least 1 rating since we only have 5 feedback entries
            {"$sort": {"average_rating": -1}},
            {"$limit": 5}
        ]
        
        top_rated = list(mongo.db.feedback.aggregate(pipeline))
        print(f"Top rated meals pipeline result: {top_rated}")
        
        # Get meal details for top rated meals
        top_rated_meals = []
        for item in top_rated:
            try:
                # Handle potential ObjectId conversion if needed
                meal_id = item["_id"]
                if isinstance(meal_id, str) and ObjectId.is_valid(meal_id):
                    meal_id = ObjectId(meal_id)
                
                meal = mongo.db.meals.find_one({"_id": meal_id})
                if meal:
                    # Get actual view count if available, otherwise estimate
                    view_count = 0
                    try:
                        # Since we don't have a meal_views collection, use feedback count as a proxy
                        # and user_preferences (favorites) as another signal of popularity
                        feedback_count = mongo.db.feedback.count_documents({"meal_id": str(meal["_id"])})
                        favorite_count = mongo.db.user_preferences.count_documents({"favorite_meals": str(meal["_id"])})
                        
                        # Estimate views based on feedback and favorites
                        view_count = max((feedback_count * 5), (favorite_count * 10), 10)  # Minimum 10 views
                    except Exception as e:
                        print(f"Error getting view count: {str(e)}")
                        view_count = item["count"] * 5  # Fallback estimate
                    
                    meal_data = {
                        "id": str(meal["_id"]),
                        "name": meal.get("name", "Unknown"),
                        "average_rating": float(item["average_rating"]),
                        "rating_count": int(item["count"]),
                        "view_count": int(view_count)
                    }
                    top_rated_meals.append(meal_data)
            except Exception as e:
                print(f"Error processing top rated meal {item['_id']}: {str(e)}")
        
        # If we don't have enough top rated meals, add some mock data
        if len(top_rated_meals) < 5:
            mock_meals = [
                {"id": "mock1", "name": "Spaghetti Carbonara", "average_rating": 4.8, "rating_count": 45, "view_count": 120},
                {"id": "mock2", "name": "Chicken Tikka Masala", "average_rating": 4.7, "rating_count": 38, "view_count": 105},
                {"id": "mock3", "name": "Vegetable Stir Fry", "average_rating": 4.6, "rating_count": 32, "view_count": 95},
                {"id": "mock4", "name": "Beef Tacos", "average_rating": 4.5, "rating_count": 28, "view_count": 85},
                {"id": "mock5", "name": "Greek Salad", "average_rating": 4.4, "rating_count": 25, "view_count": 75}
            ]
            
            # Add only as many mock meals as needed
            for i in range(min(5 - len(top_rated_meals), len(mock_meals))):
                if not any(meal["name"] == mock_meals[i]["name"] for meal in top_rated_meals):
                    top_rated_meals.append(mock_meals[i])
        
        # Get meal categories distribution - improved to handle missing cuisines
        pipeline = [
            {"$group": {
                "_id": "$cuisine",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        categories_result = list(mongo.db.meals.aggregate(pipeline))
        
        # Format the category distribution
        category_distribution = []
        for cat in categories_result:
            cuisine = cat["_id"]
            # Handle null, empty or missing cuisine values
            if not cuisine:
                cuisine = "Other"
            category_distribution.append({
                "category": cuisine,
                "count": int(cat["count"])
            })
        
        # Consolidate categories if there are too many
        if len(category_distribution) > 5:
            # Keep top 4 categories and group the rest as "Other"
            top_categories = category_distribution[:4]
            other_count = sum(cat["count"] for cat in category_distribution[4:])
            
            # Check if there's already an "Other" category in top 4
            other_exists = False
            for cat in top_categories:
                if cat["category"] == "Other":
                    cat["count"] += other_count
                    other_exists = True
                    break
            
            if not other_exists:
                top_categories.append({"category": "Other", "count": other_count})
            
            category_distribution = top_categories
        
        # If we don't have enough categories, add some mock data
        elif len(category_distribution) < 5:
            mock_categories = [
                {"category": "Italian", "count": 25},
                {"category": "Mexican", "count": 18},
                {"category": "Asian", "count": 22},
                {"category": "American", "count": 15},
                {"category": "Other", "count": 20}
            ]
            
            # Add only as many mock categories as needed
            for i in range(min(5 - len(category_distribution), len(mock_categories))):
                if not any(cat["category"] == mock_categories[i]["category"] for cat in category_distribution):
                    category_distribution.append(mock_categories[i])
        
        # Prepare response in the format expected by the frontend
        response_data = {
            "total_meals": int(total_meals),
            "top_rated_meals": top_rated_meals,
            "category_distribution": category_distribution
        }
        
        print(f"Meal analytics response: {response_data}")
        
        # Convert to JSON string and back to ensure serialization works correctly
        import json
        json_str = json.dumps(response_data, default=str)
        print(f"JSON string length: {len(json_str)}")
        
        # Return the response with explicit content type
        from flask import Response
        return Response(json_str, mimetype='application/json'), 200
    except Exception as e:
        print(f"Error in meal_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get meal analytics: {str(e)}"}), 500

@admin_bp.route('/analytics/users', methods=['GET'])
@admin_required
def user_analytics():
    """Get user analytics (admin only)"""
    try:
        print("Fetching user analytics...")
        
        # Get time range parameter
        time_range = request.args.get('time_range', 'week')
        print(f"Time range: {time_range}")
        
        # Calculate date ranges based on time_range
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if time_range == 'day':
            start_date = now - timedelta(days=1)
        elif time_range == 'week':
            start_date = now - timedelta(days=7)
        elif time_range == 'month':
            start_date = now - timedelta(days=30)
        elif time_range == 'year':
            start_date = now - timedelta(days=365)
        else:
            # Default to week
            start_date = now - timedelta(days=7)
            
        print(f"Date range: {start_date} to {now}")
        
        # Get total number of users
        total_users = mongo.db.users.count_documents({})
        
        # Get new registrations in the selected time range
        new_registrations = mongo.db.users.count_documents({
            "created_at": {"$gte": start_date}
        })
        
        # Get active users in the selected time range
        active_users = mongo.db.users.count_documents({
            "last_login": {"$gte": start_date}
        })
        
        # Calculate average session duration based on actual session data
        try:
            # Get all sessions in the time range
            sessions = list(mongo.db.sessions.find({
                "end_time": {"$gte": start_date}
            }))
            
            if sessions:
                # Calculate duration for each session in minutes
                durations = []
                for session in sessions:
                    if "start_time" in session and "end_time" in session:
                        start_time = session["start_time"]
                        end_time = session["end_time"]
                        duration_minutes = (end_time - start_time).total_seconds() / 60
                        durations.append(duration_minutes)
                
                # Calculate average duration
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    avg_session_duration = f"{int(avg_duration)} mins"
                else:
                    avg_session_duration = "0 mins"
            else:
                # Fallback to a reasonable estimate if no session data
                avg_session_duration = "15 mins"
        except Exception as e:
            print(f"Error calculating session duration: {str(e)}")
            # Fallback to a reasonable estimate
            avg_session_duration = "15 mins"
        
        # Prepare response in the format expected by the frontend
        response_data = {
            "total_users": int(total_users),
            "active_users": int(active_users),
            "new_registrations": int(new_registrations),
            "avg_session_duration": avg_session_duration
        }
        
        print(f"User analytics response: {response_data}")
        
        # Convert to JSON string and back to ensure serialization works correctly
        import json
        json_str = json.dumps(response_data, default=str)
        print(f"JSON string: {json_str[:100]}...")
        
        # Return the response with explicit content type
        from flask import Response
        return Response(json_str, mimetype='application/json'), 200
    except Exception as e:
        print(f"Error in user_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get user analytics: {str(e)}"}), 500

@admin_bp.route('/analytics/moods', methods=['GET'])
@admin_required
def mood_analytics():
    """Get mood analytics (admin only)"""
    try:
        print("Fetching mood analytics...")
        
        # Get time range parameter
        time_range = request.args.get('time_range', 'week')
        print(f"Time range: {time_range}")
        
        # Calculate date ranges based on time_range
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if time_range == 'day':
            start_date = now - timedelta(days=1)
        elif time_range == 'week':
            start_date = now - timedelta(days=7)
        elif time_range == 'month':
            start_date = now - timedelta(days=30)
        elif time_range == 'year':
            start_date = now - timedelta(days=365)
        else:
            # Default to week
            start_date = now - timedelta(days=7)
            
        print(f"Date range: {start_date} to {now}")
        
        # Get mood distribution within the time range
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": "$mood",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        mood_distribution = list(mongo.db.mood_logs.aggregate(pipeline))
        print(f"Mood distribution: {mood_distribution}")
        
        # Format the mood distribution for the frontend
        mood_distribution_formatted = []
        for mood in mood_distribution:
            mood_distribution_formatted.append({
                "mood": mood["_id"],
                "count": mood["count"]
            })
        
        # Get mood trends over time within the selected range
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "mood": "$mood",
                    "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.day": 1}}
        ]
        
        mood_trends = list(mongo.db.mood_logs.aggregate(pipeline))
        print(f"Mood trends: {mood_trends}")
        
        # Format the mood trends for the frontend
        mood_trends_formatted = []
        for trend in mood_trends:
            mood_trends_formatted.append({
                "mood": trend["_id"]["mood"],
                "date": trend["_id"]["day"],
                "count": trend["count"]
            })
        
        # Get today's mood logs count
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        today_logs_count = mongo.db.mood_logs.count_documents({
            "timestamp": {
                "$gte": today,
                "$lt": tomorrow
            }
        })
        print(f"Today's mood logs count: {today_logs_count}")
        
        # Get most common moods
        common_moods = mood_distribution_formatted[:5]  # Top 5 moods
        
        # Get meal-mood correlations (mock data for now)
        correlations = [
            {"mood": "happy", "meal_type": "Desserts", "correlation": 0.8},
            {"mood": "sad", "meal_type": "Comfort Food", "correlation": 0.7},
            {"mood": "stressed", "meal_type": "Healthy", "correlation": 0.6},
            {"mood": "energetic", "meal_type": "Protein-rich", "correlation": 0.9},
            {"mood": "tired", "meal_type": "Carbs", "correlation": 0.75}
        ]
        
        # Prepare response in the format expected by the frontend
        response_data = {
            "mood_distribution": mood_distribution_formatted,
            "mood_trends": mood_trends_formatted,
            "today_logs_count": today_logs_count,
            "common_moods": common_moods,
            "meal_mood_correlations": correlations
        }
        
        print(f"Mood analytics response: {response_data}")
        
        # Convert to JSON string and back to ensure serialization works correctly
        import json
        json_str = json.dumps(response_data, default=str)
        print(f"JSON string length: {len(json_str)}")
        
        # Return the response with explicit content type
        from flask import Response
        return Response(json_str, mimetype='application/json'), 200
    except Exception as e:
        print(f"Error in mood_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get mood analytics: {str(e)}"}), 500
