from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import datetime
from bson.objectid import ObjectId
import json
from db import mongo

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_moodeats')

# Configure MongoDB
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/moodeats')
mongo.init_app(app)

# Enable CORS
CORS(app, supports_credentials=True)

# Custom JSON encoder to handle ObjectId and datetime
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = MongoJSONEncoder

# Root route
@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to MoodEats API",
        "status": "online",
        "version": "1.0.0"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Import and register blueprints
from routes.user_routes import user_bp
from routes.meal_routes import meal_bp
from routes.mood_routes import mood_bp
from routes.admin_routes import admin_bp

app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(meal_bp, url_prefix='/api/meals')
app.register_blueprint(mood_bp, url_prefix='/api/moods')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
