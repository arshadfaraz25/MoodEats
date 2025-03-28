from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from db import mongo
from models.meal import Meal, NutritionalInfo
from models.feedback import Feedback

meal_bp = Blueprint('meal_bp', __name__)

@meal_bp.route('/', methods=['GET'])
def get_meals():
    """Get all meals with optional filtering"""
    # Parse query parameters
    cuisine = request.args.get('cuisine')
    meal_type = request.args.get('meal_type')
    dietary_tags = request.args.getlist('dietary_tags')
    mood_tags = request.args.getlist('mood_tags')
    limit = int(request.args.get('limit', 20))
    
    # Build query
    query = {}
    
    if cuisine:
        query['cuisine_type'] = cuisine
    
    if meal_type:
        query['meal_type'] = meal_type
    
    if dietary_tags:
        query['nutritional_info.dietary_tags'] = {'$in': dietary_tags}
    
    if mood_tags:
        query['mood_tags'] = {'$in': mood_tags}
    
    # Execute query
    meals = mongo.db.meals.find(query).limit(limit)
    
    # Convert to list and serialize ObjectId
    meal_list = []
    for meal in meals:
        meal['_id'] = str(meal['_id'])
        meal_list.append(meal)
    
    return jsonify(meal_list), 200

@meal_bp.route('/<meal_id>', methods=['GET'])
def get_meal(meal_id):
    """Get a specific meal by ID"""
    try:
        # Find meal in database
        meal = mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
        
        if not meal:
            return jsonify({"error": "Meal not found"}), 404
        
        # Convert ObjectId to string for JSON serialization
        meal["_id"] = str(meal["_id"])
        
        # Get feedback for this meal
        feedback_cursor = mongo.db.feedback.find({"meal_id": ObjectId(meal_id)})
        feedback_list = []
        
        for feedback in feedback_cursor:
            feedback["_id"] = str(feedback["_id"])
            feedback["user_id"] = str(feedback["user_id"])
            feedback["meal_id"] = str(feedback["meal_id"])
            if feedback.get("mood_id"):
                feedback["mood_id"] = str(feedback["mood_id"])
            feedback_list.append(feedback)
        
        # Add feedback to meal response
        meal["feedback"] = feedback_list
        
        return jsonify(meal), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@meal_bp.route('/<meal_id>/feedback', methods=['POST'])
def add_feedback(meal_id):
    """Add feedback for a meal"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    # Check if required fields are present
    if not data or 'rating' not in data:
        return jsonify({"error": "Rating is required"}), 400
    
    # Validate rating
    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400
    
    # Create feedback object
    feedback = Feedback(
        user_id=ObjectId(user_id),
        meal_id=ObjectId(meal_id),
        rating=rating,
        comment=data.get('comment'),
        mood_id=ObjectId(data['mood_id']) if data.get('mood_id') else None
    )
    
    # Insert feedback into database
    feedback_id = mongo.db.feedback.insert_one(feedback.to_dict()).inserted_id
    
    return jsonify({
        "message": "Feedback added successfully",
        "feedback_id": str(feedback_id)
    }), 201

@meal_bp.route('/search', methods=['GET'])
def search_meals():
    """Search for meals by name or ingredients"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify([]), 200
    
    # Search by name or ingredients
    meals = mongo.db.meals.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"ingredients": {"$regex": query, "$options": "i"}}
        ]
    }).limit(limit)
    
    # Convert to list and serialize ObjectId
    meal_list = []
    for meal in meals:
        meal['_id'] = str(meal['_id'])
        meal_list.append(meal)
    
    return jsonify(meal_list), 200

@meal_bp.route('/random', methods=['GET'])
def get_random_meals():
    """Get random meals"""
    limit = int(request.args.get('limit', 10))
    
    # MongoDB aggregation to get random documents
    pipeline = [{"$sample": {"size": limit}}]
    meals = mongo.db.meals.aggregate(pipeline)
    
    # Convert to list and serialize ObjectId
    meal_list = []
    for meal in meals:
        meal['_id'] = str(meal['_id'])
        meal_list.append(meal)
    
    return jsonify(meal_list), 200
