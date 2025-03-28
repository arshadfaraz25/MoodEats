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
            return jsonify({"error": "Unauthorized"}), 401
        
        user_id = session['user_id']
        
        # Check if user is an admin
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user or not user.get('is_admin', False):
            return jsonify({"error": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)"""
    limit = int(request.args.get('limit', 100))
    
    # Get users from database
    users = mongo.db.users.find().limit(limit)
    
    # Convert to list and serialize ObjectId
    user_list = []
    for user in users:
        user['_id'] = str(user['_id'])
        # Remove password hash for security
        if 'password_hash' in user:
            del user['password_hash']
        user_list.append(user)
    
    return jsonify(user_list), 200

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

@admin_bp.route('/analytics/users', methods=['GET'])
@admin_required
def user_analytics():
    """Get user analytics (admin only)"""
    # Get total number of users
    total_users = mongo.db.users.count_documents({})
    
    # Get new users in the last 30 days
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_users = mongo.db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    # Get active users (logged in within the last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    active_users = mongo.db.users.count_documents({"last_login": {"$gte": seven_days_ago}})
    
    return jsonify({
        "total_users": total_users,
        "new_users_last_30_days": new_users,
        "active_users_last_7_days": active_users
    }), 200

@admin_bp.route('/analytics/meals', methods=['GET'])
@admin_required
def meal_analytics():
    """Get meal analytics (admin only)"""
    # Get total number of meals
    total_meals = mongo.db.meals.count_documents({})
    
    # Get top rated meals
    pipeline = [
        {"$group": {
            "_id": "$meal_id",
            "average_rating": {"$avg": "$rating"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gte": 3}}},  # At least 3 ratings
        {"$sort": {"average_rating": -1}},
        {"$limit": 5}
    ]
    
    top_rated = list(mongo.db.feedback.aggregate(pipeline))
    
    # Get meal details for top rated meals
    top_meals = []
    for item in top_rated:
        meal = mongo.db.meals.find_one({"_id": item["_id"]})
        if meal:
            meal["_id"] = str(meal["_id"])
            meal["average_rating"] = item["average_rating"]
            meal["rating_count"] = item["count"]
            top_meals.append(meal)
    
    # Get most favorited meals
    pipeline = [
        {"$unwind": "$favorite_meals"},
        {"$group": {
            "_id": "$favorite_meals",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    
    most_favorited = list(mongo.db.user_preferences.aggregate(pipeline))
    
    # Get meal details for most favorited meals
    favorite_meals = []
    for item in most_favorited:
        meal = mongo.db.meals.find_one({"_id": item["_id"]})
        if meal:
            meal["_id"] = str(meal["_id"])
            meal["favorite_count"] = item["count"]
            favorite_meals.append(meal)
    
    return jsonify({
        "total_meals": total_meals,
        "top_rated_meals": top_meals,
        "most_favorited_meals": favorite_meals
    }), 200

@admin_bp.route('/analytics/moods', methods=['GET'])
@admin_required
def mood_analytics():
    """Get mood analytics (admin only)"""
    # Get mood distribution
    pipeline = [
        {"$group": {
            "_id": "$mood",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    mood_distribution = list(mongo.db.mood_logs.aggregate(pipeline))
    
    # Get mood trends over time (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": thirty_days_ago}}},
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
    
    # Format the results
    trends_formatted = []
    for trend in mood_trends:
        trends_formatted.append({
            "mood": trend["_id"]["mood"],
            "date": trend["_id"]["day"],
            "count": trend["count"]
        })
    
    return jsonify({
        "mood_distribution": mood_distribution,
        "mood_trends": trends_formatted
    }), 200
