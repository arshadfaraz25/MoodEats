from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from db import mongo
from models.mood_log import MoodLog
from models.recommendation_engine import RecommendationEngine
from models.database_manager import DatabaseManager
from datetime import datetime, timedelta

mood_bp = Blueprint('mood_bp', __name__)

@mood_bp.route('/log', methods=['POST'])
def log_mood():
    """Log a user's mood"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    # Check if required fields are present
    if not data or not data.get('mood'):
        return jsonify({"error": "Mood is required"}), 400
    
    # Check for recent duplicate entries (within the last 5 seconds)
    current_time = datetime.now()
    five_seconds_ago = current_time - timedelta(seconds=5)
    
    recent_duplicate = mongo.db.mood_logs.find_one({
        "user_id": ObjectId(user_id),
        "mood": data['mood'],
        "timestamp": {"$gte": five_seconds_ago}
    })
    
    if recent_duplicate:
        # Return the existing entry instead of creating a duplicate
        recent_duplicate['_id'] = str(recent_duplicate['_id'])
        recent_duplicate['user_id'] = str(recent_duplicate['user_id'])
        return jsonify({
            "message": "Mood already logged",
            "log_id": recent_duplicate['_id']
        }), 200
    
    # Create mood log
    mood_log = MoodLog(
        user_id=ObjectId(user_id),
        mood=data['mood'],
        notes=data.get('notes')
    )
    
    # Insert mood log into database
    log_id = mongo.db.mood_logs.insert_one(mood_log.to_dict()).inserted_id
    
    return jsonify({
        "message": "Mood logged successfully",
        "log_id": str(log_id)
    }), 201

@mood_bp.route('/history', methods=['GET'])
def get_mood_history():
    """Get a user's mood history"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    limit = request.args.get('limit', '10')
    
    # Convert limit to integer, handling the case where it might be a string
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    # Get mood logs from database
    query = {"user_id": ObjectId(user_id)}
    
    # Count total logs for this user
    total_logs = mongo.db.mood_logs.count_documents(query)
    print(f"Found {total_logs} mood logs for user {user_id}")
    
    # If limit is 0, return all mood logs (no limit)
    if limit == 0:
        mood_logs = list(mongo.db.mood_logs.find(query).sort("timestamp", -1))
        print(f"Returning all {len(mood_logs)} mood logs")
    else:
        mood_logs = list(mongo.db.mood_logs.find(query).sort("timestamp", -1).limit(limit))
        print(f"Returning {len(mood_logs)} mood logs (limited to {limit})")
    
    # Convert to list and serialize ObjectId
    log_list = []
    for log in mood_logs:
        log['_id'] = str(log['_id'])
        log['user_id'] = str(log['user_id'])
        log_list.append(log)
    
    return jsonify(log_list), 200

@mood_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get meal recommendations based on mood"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    mood = request.args.get('mood')
    limit = int(request.args.get('limit', 10))
    
    if not mood:
        return jsonify({"error": "Mood parameter is required"}), 400
    
    # Create database manager and recommendation engine
    db_manager = DatabaseManager(mongo)
    recommendation_engine = RecommendationEngine(db_manager)
    
    # Get recommendations
    recommendations = recommendation_engine.get_recommendations(
        user_id=ObjectId(user_id),
        mood=mood,
        limit=limit
    )
    
    # Remove duplicates by meal ID
    unique_recommendations = []
    seen_ids = set()
    
    for meal in recommendations:
        meal_id = str(meal.meal_id)
        if meal_id not in seen_ids:
            seen_ids.add(meal_id)
            unique_recommendations.append(meal)
    
    print(f"Original recommendations: {len(recommendations)}, After deduplication: {len(unique_recommendations)}")
    
    # Convert to list of dictionaries for JSON serialization
    recommendation_list = []
    for meal in unique_recommendations:
        meal_dict = meal.to_dict()
        meal_dict['_id'] = str(meal_dict['_id'])
        recommendation_list.append(meal_dict)
    
    return jsonify(recommendation_list), 200

@mood_bp.route('/moods', methods=['GET'])
def get_available_moods():
    """Get list of available moods"""
    # This could be expanded in the future, but for now we'll return a static list
    moods = [
        {"id": "happy", "name": "Happy", "emoji": "😊", "description": "Feeling joyful and content"},
        {"id": "sad", "name": "Sad", "emoji": "😢", "description": "Feeling down or blue"},
        {"id": "stressed", "name": "Stressed", "emoji": "😰", "description": "Feeling anxious or overwhelmed"},
        {"id": "energetic", "name": "Energetic", "emoji": "⚡", "description": "Feeling full of energy and vigor"},
        {"id": "tired", "name": "Tired", "emoji": "😴", "description": "Feeling fatigued or exhausted"},
        {"id": "anxious", "name": "Anxious", "emoji": "😟", "description": "Feeling worried or nervous"},
        {"id": "nostalgic", "name": "Nostalgic", "emoji": "🕰️", "description": "Feeling sentimental about the past"},
        {"id": "relaxed", "name": "Relaxed", "emoji": "😌", "description": "Feeling calm and at ease"}
    ]
    
    return jsonify(moods), 200
