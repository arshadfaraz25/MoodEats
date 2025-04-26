# MoodEats Design Patterns Documentation

## 1. Introduction

MoodEats is a web application designed to enhance meal planning by recommending meals based on users' emotional states. This document outlines the key design patterns implemented in the MoodEats application, focusing on the backend architecture.

### 1.1 Purpose of This Document

This document serves as a comprehensive guide to the design patterns used in the MoodEats application. It aims to:
- Document the architectural decisions made during development
- Provide a reference for developers working on the system
- Facilitate understanding of the codebase for new team members
- Serve as a basis for future enhancements and refactoring

### 1.2 Target Audience

This document is intended for:
- Software developers working on the MoodEats application
- System architects evaluating the application design
- Technical leads overseeing the development process
- Quality assurance engineers testing the application

## 2. Architectural Overview

MoodEats follows a layered architecture with clear separation of concerns:

### 2.1 Presentation Layer
- **Components**: Flask routes and blueprints
- **Responsibility**: Handling HTTP requests, input validation, and response formatting
- **Key Files**: Files in the `routes` directory (user_routes.py, meal_routes.py, mood_routes.py, admin_routes.py)

### 2.2 Business Logic Layer
- **Components**: Service classes and recommendation engine
- **Responsibility**: Implementing business rules and application logic
- **Key Files**: recommendation_engine.py and service-related components

### 2.3 Data Access Layer
- **Components**: Database manager and model classes
- **Responsibility**: Providing an abstraction over the database operations
- **Key Files**: database_manager.py, user.py, meal.py, mood_log.py, feedback.py, user_preferences.py

### 2.4 Data Storage Layer
- **Components**: MongoDB database
- **Responsibility**: Persistent storage of application data
- **Configuration**: Defined in app.py and db.py

### 2.5 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      MoodEats Application                        │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│  │ Presentation│     │ Business    │     │ Data Access │        │
│  │ Layer       │────►│ Logic Layer │────►│ Layer       │        │
│  │ (Routes)    │     │ (Services)  │     │ (Models)    │        │
│  └─────────────┘     └─────────────┘     └──────┬──────┘        │
│                                                 │               │
│                                                 ▼               │
│                                          ┌─────────────┐        │
│                                          │ Data Storage│        │
│                                          │ Layer (DB)  │        │
│                                          └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Design Patterns Implemented

### 3.1 Singleton Pattern

**Intent**: Ensures a class has only one instance and provides a global point of access to it.

**Problem Addressed**: 
- Need for a single, shared database connection across the application
- Avoiding resource duplication and ensuring consistent state

**Implementation in MoodEats**:
- The MongoDB client in `db.py` is implemented as a singleton to ensure a single database connection is shared across the application.
- The Flask application instance in `app.py` also follows this pattern.

**How It's Used in MoodEats**:
The Singleton pattern is crucial for database connectivity in MoodEats. By maintaining a single MongoDB connection instance, the application avoids the overhead of creating multiple database connections, which would consume unnecessary resources and potentially lead to connection pool exhaustion. The pattern ensures that all components access the same database connection, maintaining consistency across the application.

The implementation is straightforward but effective:
1. A single `mongo` instance is created in `db.py`
2. This instance is imported wherever database access is needed
3. The `init_app()` method is called only once during application initialization
4. All subsequent database operations use this shared instance

**Code Example**:
```python
# db.py
from flask_pymongo import PyMongo

# Singleton instance of PyMongo
mongo = PyMongo()

# In app.py
from db import mongo
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/moodeats')
mongo.init_app(app)
```

**Benefits**:
- Reduced memory footprint by avoiding multiple database connections
- Consistent application state across different components
- Centralized configuration management

**Potential Drawbacks**:
- Global state can make testing more difficult
- Thread safety concerns in concurrent environments

**Diagram**:
```
┌───────────────────────────────────┐
│             PyMongo               │
├───────────────────────────────────┤
│ - static instance: mongo          │
├───────────────────────────────────┤
│ + init_app(app)                   │
└───────────────────────────────────┘
      ▲
      │ imports
      │
┌─────┴─────────────────────────────┐
│             app.py                │
├───────────────────────────────────┤
│ - app: Flask                      │
├───────────────────────────────────┤
│ + register_blueprint()            │
└───────────────────────────────────┘
```

**Relationships**:
- **Imports**: The Flask application imports the singleton MongoDB instance
- **Initialization**: The Flask app initializes the MongoDB connection once
- **Usage**: All components use the same MongoDB connection throughout the application lifecycle

### 3.2 Facade Pattern

**Intent**: Provides a simplified interface to a complex subsystem.

**Problem Addressed**:
- Complexity of direct database interactions
- Need for a unified API for database operations
- Decoupling business logic from data access details

**Implementation in MoodEats**:
- The `DatabaseManager` class provides a simplified interface to the MongoDB operations, abstracting away the complexity of database interactions.
- It offers a unified API for all database operations related to users, meals, moods, and feedback.

**How It's Used in MoodEats**:
The Facade pattern is implemented through the `DatabaseManager` class, which serves as a unified interface for all database operations. Instead of having route handlers directly interact with MongoDB collections, they use the DatabaseManager's methods, which encapsulate the complexity of database queries, document conversion, and error handling.

This implementation:
1. Centralizes all database access logic in one place
2. Provides domain-specific methods that map to business operations
3. Abstracts away MongoDB-specific details from the rest of the application
4. Makes the codebase more maintainable by isolating database access code

**Code Example**:
```python
# Example from database_manager.py
class DatabaseManager:
    def __init__(self, mongo_client):
        self.db = mongo_client.db
    
    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        user_dict = self.db.users.find_one({"_id": ObjectId(user_id)})
        return User.from_dict(user_dict) if user_dict else None
    
    def get_meal_by_id(self, meal_id):
        """Get a meal by ID"""
        meal_dict = self.db.meals.find_one({"_id": ObjectId(meal_id)})
        return Meal.from_dict(meal_dict) if meal_dict else None
        
    # Many more methods providing a unified interface to the database
```

**Client Code Using the Facade**:
```python
# Example usage in routes/user_routes.py
@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    db_manager = DatabaseManager(mongo)
    user = db_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())
```

**Benefits**:
- Simplified client code that doesn't need to understand database details
- Centralized place for database access logic
- Easier to change database implementation if needed
- Improved code organization and maintainability

**Potential Drawbacks**:
- May introduce an unnecessary layer if the subsystem is not complex
- Can hide important details from clients

**Diagram**:
```
┌───────────────────────────┐       ┌───────────────────────────────────────┐
│      Routes               │       │           DatabaseManager              │
├───────────────────────────┤       ├───────────────────────────────────────┤
│                           │       │ - db: mongo.db                         │
├───────────────────────────┤       ├───────────────────────────────────────┤
│ + get_user(user_id)       │──────►│ + create_user(user)                    │
│ + create_user(data)       │       │ + get_user_by_id(user_id)              │
│ + get_meal(meal_id)       │       │ + get_user_by_email(email)             │
│ + create_meal(data)       │       │ + update_user(user)                    │
└───────────────────────────┘       │ + delete_user(user_id)                 │
                                    │ + create_meal(meal)                    │
                                    │ + get_meal_by_id(meal_id)              │
                                    │ + get_meals_by_ids(meal_ids)           │
                                    │ + get_meals_by_query(query, limit)     │
                                    │ + get_random_meals(limit)              │
                                    │ + update_meal(meal)                    │
                                    │ + delete_meal(meal_id)                 │
                                    │ + create_mood_log(user_id, mood, notes)│
                                    │ + get_mood_logs_by_user(user_id, limit)│
                                    │ + create_feedback(feedback)            │
                                    │ + get_user_feedback(user_id, limit)    │
                                    │ + get_meal_feedback(meal_id, limit)    │
                                    └─────────────────┬─────────────────────┘
                                                      │
                                                      │ uses
                                                      ▼
                                    ┌───────────────────────────────────────┐
                                    │             MongoDB                   │
                                    ├───────────────────────────────────────┤
                                    │ - users                               │
                                    │ - meals                               │
                                    │ - mood_logs                           │
                                    │ - feedback                            │
                                    │ - user_preferences                    │
                                    └───────────────────────────────────────┘
```

**Relationships**:
- **Client-Facade**: Route handlers use the DatabaseManager as a facade to access database functionality
- **Facade-Subsystem**: DatabaseManager encapsulates and simplifies MongoDB operations
- **Abstraction**: The facade provides a domain-specific API that hides the complexity of the underlying database operations

### 3.3 Factory Method Pattern

**Intent**: Creates objects without specifying the exact class to create.

**Problem Addressed**:
- Need to convert between database documents and domain objects
- Decoupling object creation from object use
- Supporting different object creation strategies

**Implementation in MoodEats**:
- Domain classes like `User`, `Meal`, and `MoodLog` implement static `from_dict()` methods that serve as factory methods.
- These methods create domain objects from database documents (dictionaries).

**How It's Used in MoodEats**:
The Factory Method pattern is implemented through static `from_dict()` methods in domain classes. When data is retrieved from MongoDB, it's in dictionary format. The factory methods transform these dictionaries into proper domain objects with all their methods and behaviors.

This implementation:
1. Centralizes the creation logic for each domain object type
2. Handles data type conversions (e.g., string IDs to ObjectIds, ISO strings to datetime objects)
3. Provides a consistent interface for object creation across the application
4. Makes it easy to modify the creation process without affecting client code

**Code Example**:
```python
# Example from models/user.py
class User:
    def __init__(self, email, password_hash, name, user_id=None, created_at=None):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert User object to dictionary for database storage"""
        return {
            "_id": self.user_id,
            "email": self.email,
            "password_hash": self.password_hash,
            "name": self.name,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(user_dict):
        """Factory method to create User from dictionary"""
        if not user_dict:
            return None
        return User(
            email=user_dict["email"],
            password_hash=user_dict["password_hash"],
            name=user_dict["name"],
            user_id=user_dict.get("_id"),
            created_at=user_dict.get("created_at")
        )
```

**Client Code Using the Factory**:
```python
# In database_manager.py
def get_user_by_id(self, user_id):
    user_dict = self.db.users.find_one({"_id": ObjectId(user_id)})
    # Factory method creates User object from dictionary
    return User.from_dict(user_dict) if user_dict else None
```

**Benefits**:
- Encapsulation of object creation logic
- Consistent object creation across the application
- Easy to modify creation process without affecting client code
- Support for object validation during creation

**Potential Drawbacks**:
- Additional complexity for simple objects
- Potential duplication of code across similar factory methods

**Relationships**:
- **Document-to-Object**: The factory method transforms database documents (dictionaries) into domain objects
- **Encapsulation**: The creation logic is encapsulated within the class itself
- **Consistency**: All objects of a given type are created through the same factory method

### 3.4 Strategy Pattern

**Intent**: Defines a family of algorithms, encapsulates each one, and makes them interchangeable.

**Problem Addressed**:
- Need for different recommendation algorithms based on context
- Avoiding complex conditional logic in recommendation code
- Supporting extensibility for future recommendation strategies

**Implementation in MoodEats**:
- The `RecommendationEngine` class implements different recommendation strategies:
  - Mood-based recommendations
  - Personalized recommendations based on user history
  - Default recommendations when other strategies are not applicable

**How It's Used in MoodEats**:
The Strategy pattern is implemented within the `RecommendationEngine` class, which provides different methods for generating meal recommendations. While not implemented as separate strategy classes, the different recommendation methods act as encapsulated algorithms that can be selected at runtime.

This implementation:
1. Allows the application to choose the appropriate recommendation strategy based on context
2. Encapsulates each recommendation algorithm in its own method
3. Makes it easy to add new recommendation strategies in the future
4. Simplifies the client code by providing a unified interface for recommendations

**Code Example**:
```python
# From recommendation_engine.py
class RecommendationEngine:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.mood_food_mapping = {
            "happy": ["comfort", "celebration", "energizing"],
            "sad": ["comfort", "indulgent", "warming"],
            "stressed": ["calming", "simple", "nutritious"],
            "energetic": ["protein-rich", "complex-carbs", "refreshing"],
            "tired": ["energizing", "quick", "nutrient-dense"]
        }
    
    # Strategy 1: Mood-based recommendations
    def get_recommendations(self, user_id, mood, limit=10):
        user_prefs = self.db_manager.get_user_preferences(user_id)
        
        # Log the mood for future analysis
        self.db_manager.create_mood_log(user_id, mood)
        
        # Get food tags associated with the mood
        mood_tags = self.mood_food_mapping.get(mood.lower(), [])
        
        # If we have mood tags, use them for recommendations
        if mood_tags:
            query = {"mood_tags": {"$in": mood_tags}}
            if user_prefs and user_prefs.get("dietary_restrictions"):
                # Filter out meals that don't meet dietary restrictions
                query["dietary_info.restrictions"] = {"$nin": user_prefs["dietary_restrictions"]}
            
            meals = self.db_manager.get_meals_by_query(query, limit)
            
            # If we found enough meals, return them
            if len(meals) >= limit:
                return meals
        
        # Fallback to personalized recommendations if mood-based didn't work
        return self.get_personalized_recommendations(user_id, limit)
    
    # Strategy 2: Personalized recommendations based on user history
    def get_personalized_recommendations(self, user_id, limit=10):
        user_prefs = self.db_manager.get_user_preferences(user_id)
        
        # If we have user preferences, use them
        if user_prefs:
            query = {}
            
            if user_prefs.get("favorite_cuisines"):
                query["cuisine_type"] = {"$in": user_prefs["favorite_cuisines"]}
            
            if user_prefs.get("dietary_restrictions"):
                query["dietary_info.restrictions"] = {"$nin": user_prefs["dietary_restrictions"]}
            
            meals = self.db_manager.get_meals_by_query(query, limit)
            
            # If we found enough meals, return them
            if len(meals) >= limit:
                return meals
        
        # Fallback to default recommendations
        return self._get_default_recommendations(limit)
    
    # Strategy 3: Default recommendations when other strategies don't apply
    def _get_default_recommendations(self, limit=10):
        # Just get random meals as a last resort
        return self.db_manager.get_random_meals(limit)
```

**Client Code Using the Strategy**:
```python
# In routes/mood_routes.py
@mood_bp.route('/recommendations', methods=['POST'])
def get_mood_recommendations():
    data = request.json
    user_id = data.get('user_id')
    mood = data.get('mood')
    
    # Create recommendation engine with injected database manager
    db_manager = DatabaseManager(mongo)
    recommendation_engine = RecommendationEngine(db_manager)
    
    # Use the appropriate strategy based on input
    if mood:
        # Use mood-based recommendation strategy
        recommendations = recommendation_engine.get_recommendations(user_id, mood)
    else:
        # Use personalized recommendation strategy
        recommendations = recommendation_engine.get_personalized_recommendations(user_id)
    
    return jsonify([meal.to_dict() for meal in recommendations])
```

**Benefits**:
- Flexibility to choose different recommendation algorithms at runtime
- Encapsulation of algorithm-specific logic
- Easy to add new recommendation strategies
- Simplified client code

**Potential Drawbacks**:
- Not implemented as separate strategy classes, which could improve separation of concerns
- Some duplication of code between strategies

**Relationships**:
- **Context-Strategy**: The route handlers select which recommendation strategy to use based on input parameters
- **Strategy Hierarchy**: Different recommendation methods implement different algorithms for the same task
- **Fallback Chain**: Strategies can fall back to other strategies when they don't produce sufficient results

### 3.5 Repository Pattern

**Intent**: Mediates between the domain and data mapping layers, acting like an in-memory collection of domain objects.

**Problem Addressed**:
- Decoupling domain logic from data access logic
- Centralizing data access code
- Providing a consistent interface for data operations

**Implementation in MoodEats**:
- The `DatabaseManager` class acts as a repository, providing methods for CRUD operations on domain objects.
- It abstracts away the details of MongoDB operations, providing a domain-focused interface.

**How It's Used in MoodEats**:
The Repository pattern is implemented through the `DatabaseManager` class, which serves as a centralized repository for all data access operations. While not divided into separate repositories for each domain entity, it provides entity-specific methods that encapsulate the data access logic.

This implementation:
1. Centralizes all data access code in one place
2. Provides a domain-focused interface that hides database details
3. Makes it easy to change the underlying database implementation
4. Simplifies testing by allowing the repository to be mocked

**Code Example**:
```python
# From database_manager.py
class DatabaseManager:
    def __init__(self, mongo_client):
        self.db = mongo_client.db
    
    # User repository methods
    def create_user(self, user):
        user_dict = user.to_dict()
        result = self.db.users.insert_one(user_dict)
        return result.inserted_id
    
    def get_user_by_id(self, user_id):
        user_dict = self.db.users.find_one({"_id": ObjectId(user_id)})
        return User.from_dict(user_dict) if user_dict else None
    
    def update_user(self, user):
        user_dict = user.to_dict()
        user_id = user_dict.pop("_id")
        self.db.users.update_one({"_id": user_id}, {"$set": user_dict})
    
    def delete_user(self, user_id):
        self.db.users.delete_one({"_id": ObjectId(user_id)})
    
    # Meal repository methods
    def create_meal(self, meal):
        meal_dict = meal.to_dict()
        result = self.db.meals.insert_one(meal_dict)
        return result.inserted_id
    
    def get_meal_by_id(self, meal_id):
        meal_dict = self.db.meals.find_one({"_id": ObjectId(meal_id)})
        return Meal.from_dict(meal_dict) if meal_dict else None
    
    # More repository methods for other entities...
```

**Client Code Using the Repository**:
```python
# In routes/user_routes.py
@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    db_manager = DatabaseManager(mongo)
    user = db_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())
```

**Benefits**:
- Centralized data access logic
- Domain-focused interface
- Decoupling of domain logic from data access details
- Easier testing through mocking

**Potential Drawbacks**:
- Not divided into separate repositories for each entity
- Potential for a large class with many responsibilities

**Relationships**:
- **Domain-Repository**: Domain objects are persisted and retrieved through the repository
- **Repository-Database**: The repository encapsulates all interactions with the database
- **Client-Repository**: Client code interacts with domain objects through the repository interface

### 3.6 Blueprint Pattern (Flask-specific)

**Intent**: Organizes a Flask application into modular components.

**Problem Addressed**:
- Organizing routes by functionality
- Avoiding a monolithic application structure
- Supporting team development with clear boundaries

**Implementation in MoodEats**:
- The MoodEats backend uses Flask blueprints to organize routes by functionality:
  - `user_bp` for user-related routes
  - `meal_bp` for meal-related routes
  - `mood_bp` for mood and recommendation routes
  - `admin_bp` for administrative routes

**How It's Used in MoodEats**:
The Blueprint pattern is implemented using Flask's built-in blueprint functionality. Each blueprint encapsulates a set of related routes, making the application more modular and easier to maintain.

This implementation:
1. Organizes routes by domain functionality
2. Provides a clear structure for the application
3. Allows for team development with clear boundaries
4. Makes it easier to maintain and extend the application

**Code Example**:
```python
# In routes/user_routes.py
from flask import Blueprint, request, jsonify

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    # Implementation...

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    # Implementation...

# In app.py
from routes.user_routes import user_bp
from routes.meal_routes import meal_bp
from routes.mood_routes import mood_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
# Configuration...

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(meal_bp)
app.register_blueprint(mood_bp)
app.register_blueprint(admin_bp)
```

**Benefits**:
- Modular application structure
- Clear separation of concerns
- Easier maintenance and extension
- Support for team development

**Potential Drawbacks**:
- Overhead for very small applications
- Potential for duplication across blueprints

**Relationships**:
- **App-Blueprint**: The Flask app registers multiple blueprints
- **Blueprint-Routes**: Each blueprint contains related route handlers
- **URL Prefix**: Blueprints organize routes under specific URL prefixes

### 3.7 Adapter Pattern

**Intent**: Converts the interface of a class into another interface clients expect.

**Problem Addressed**:
- Incompatibility between MongoDB data types and JSON serialization
- Need to convert between different data formats
- Supporting legacy interfaces or external services

**Implementation in MoodEats**:
- The `MongoJSONEncoder` class adapts MongoDB-specific data types (like `ObjectId` and `datetime`) to be JSON-serializable.
- This allows for seamless conversion of MongoDB documents to JSON responses.

**How It's Used in MoodEats**:
The Adapter pattern is implemented through the `MongoJSONEncoder` class, which adapts MongoDB-specific data types to be JSON-serializable. This is crucial for returning MongoDB documents as JSON responses in the API.

This implementation:
1. Extends the standard `json.JSONEncoder` class
2. Overrides the `default` method to handle MongoDB-specific types
3. Converts `ObjectId` to strings and `datetime` to ISO format
4. Allows for seamless JSON serialization of MongoDB documents

**Code Example**:
```python
# From utils/json_encoder.py
from bson import ObjectId
from datetime import datetime
import json

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)

# In app.py
from utils.json_encoder import MongoJSONEncoder

app = Flask(__name__)
app.json_encoder = MongoJSONEncoder
```

**Client Code Using the Adapter**:
```python
# In routes/user_routes.py
@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    db_manager = DatabaseManager(mongo)
    user = db_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # The MongoJSONEncoder automatically handles ObjectId and datetime conversion
    return jsonify(user.to_dict())
```

**Benefits**:
- Seamless conversion between incompatible interfaces
- Centralized handling of data type conversions
- No need to manually convert data types in route handlers

**Potential Drawbacks**:
- Additional complexity for simple applications
- Potential performance overhead for large responses

**Relationships**:
- **Adapter-Adaptee**: The MongoJSONEncoder adapts MongoDB data types
- **Client-Adapter**: Route handlers use the adapter indirectly through Flask's JSON serialization
- **Interface Conversion**: MongoDB types are converted to JSON-compatible types

### 3.8 Data Transfer Object (DTO) Pattern

**Intent**: Carries data between processes, reducing the number of method calls.

**Problem Addressed**:
- Need to transfer data between application layers
- Reducing the number of database calls
- Providing a clean interface for client-server communication

**Implementation in MoodEats**:
- Domain objects like `User`, `Meal`, and `MoodLog` implement `to_dict()` methods that convert them to dictionaries (DTOs) for API responses.
- These DTOs contain only the data needed by the client, without internal implementation details.

**How It's Used in MoodEats**:
The DTO pattern is implemented through the `to_dict()` methods in domain classes. These methods convert domain objects with their complex behaviors and relationships into simple dictionaries that can be easily serialized to JSON for API responses.

This implementation:
1. Separates the domain model from the data transfer representation
2. Allows for customization of what data is exposed to clients
3. Simplifies serialization for API responses
4. Provides a clear boundary between the domain and presentation layers

**Code Example**:
```python
# From models/user.py
class User:
    def __init__(self, email, password_hash, name, user_id=None, created_at=None):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert User object to dictionary (DTO) for API response"""
        return {
            "_id": self.user_id,
            "email": self.email,
            # Note: password_hash is excluded for security
            "name": self.name,
            "created_at": self.created_at
        }
    
    def to_secure_dict(self):
        """Convert User object to secure dictionary (DTO) with password hash"""
        dto = self.to_dict()
        dto["password_hash"] = self.password_hash
        return dto
```

**Client Code Using the DTO**:
```python
# In routes/user_routes.py
@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    db_manager = DatabaseManager(mongo)
    user = db_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Convert domain object to DTO for API response
    return jsonify(user.to_dict())
```

**Benefits**:
- Clean separation between domain model and API representation
- Control over what data is exposed to clients
- Simplified serialization for API responses
- Ability to version APIs without changing domain models

**Potential Drawbacks**:
- Duplication between domain model and DTO
- Additional mapping code required

**Relationships**:
- **Domain-DTO**: Domain objects are converted to DTOs for transfer
- **DTO-Client**: DTOs are serialized to JSON for client consumption
- **Data Filtering**: The DTO pattern allows for filtering sensitive or unnecessary data

### 3.9 Dependency Injection

**Intent**: Decouples the creation of objects from their use.

**Problem Addressed**:
- Reducing tight coupling between components
- Improving testability
- Centralizing dependency management

**Implementation in MoodEats**:
- The `RecommendationEngine` receives a `DatabaseManager` instance through its constructor, demonstrating dependency injection.
- This allows for better testability and loose coupling between components.

**How It's Used in MoodEats**:
Dependency Injection is implemented through constructor injection in classes like `RecommendationEngine`. Instead of creating their dependencies internally, these classes receive them through their constructors.

This implementation:
1. Decouples component creation from component use
2. Makes testing easier by allowing dependencies to be mocked
3. Centralizes dependency creation in route handlers
4. Improves flexibility by allowing different implementations to be injected

**Code Example**:
```python
# From recommendation_engine.py
class RecommendationEngine:
    def __init__(self, db_manager):
        # Dependency injected through constructor
        self.db_manager = db_manager
        # Rest of initialization...
    
    def get_recommendations(self, user_id, mood, limit=10):
        # Uses the injected db_manager
        user_prefs = self.db_manager.get_user_preferences(user_id)
        # Rest of implementation...
```

**Client Code Using Dependency Injection**:
```python
# In routes/mood_routes.py
@mood_bp.route('/recommendations', methods=['POST'])
def get_mood_recommendations():
    data = request.json
    user_id = data.get('user_id')
    mood = data.get('mood')
    
    # Create dependencies
    db_manager = DatabaseManager(mongo)
    
    # Inject dependencies
    recommendation_engine = RecommendationEngine(db_manager)
    
    # Use the component
    recommendations = recommendation_engine.get_recommendations(user_id, mood)
    
    return jsonify([meal.to_dict() for meal in recommendations])
```

**Benefits**:
- Loose coupling between components
- Improved testability
- Flexibility to change implementations
- Clear dependency relationships

**Potential Drawbacks**:
- More complex setup code
- No centralized dependency container in the current implementation

**Relationships**:
- **Injector-Component**: Route handlers inject dependencies into components
- **Component-Dependency**: Components use injected dependencies rather than creating them
- **Loose Coupling**: Components depend on interfaces rather than concrete implementations

## 4. Benefits of Design Patterns in MoodEats

### 4.1 Maintainability
- **Separation of Concerns**: Each pattern focuses on a specific aspect of the system
- **Modular Design**: Changes can be made to one component without affecting others
- **Standardized Structure**: Familiar patterns make the codebase easier to understand
- **Reduced Technical Debt**: Well-structured code is easier to maintain over time

### 4.2 Scalability
- **Loose Coupling**: Components can be modified or replaced independently
- **Extensibility**: New features can be added without major restructuring
- **Performance Optimization**: Patterns like Singleton help manage resource usage
- **Distributed Development**: Team members can work on different components simultaneously

### 4.3 Testability
- **Dependency Injection**: Makes it easier to substitute real components with mocks
- **Clear Interfaces**: Well-defined interfaces simplify test setup
- **Isolated Components**: Each component can be tested independently
- **Predictable Behavior**: Design patterns provide consistent behavior that's easier to test

### 4.4 Code Reusability
- **Standardized Interfaces**: Components with standard interfaces are easier to reuse
- **Encapsulated Functionality**: Patterns encapsulate specific functionality that can be reused
- **Reduced Duplication**: Common functionality is centralized
- **Improved Abstraction**: Higher-level abstractions make code more reusable

## 5. Conclusion

The MoodEats application implements several design patterns that contribute to a well-structured, maintainable, and scalable backend architecture. These patterns help manage complexity, improve code organization, and facilitate future enhancements to the system.

By following established design patterns, MoodEats achieves a balance between flexibility and structure, allowing for both stability in the current implementation and adaptability for future requirements.

## 6. References

1. Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software.
2. Fowler, M. (2002). Patterns of Enterprise Application Architecture.
3. Flask Documentation: https://flask.palletsprojects.com/
4. MongoDB Documentation: https://docs.mongodb.com/
5. PyMongo Documentation: https://pymongo.readthedocs.io/

## 7. UML Diagrams of Design Patterns

### 7.1 Singleton Pattern UML

```
┌───────────────────────────────────┐
│             PyMongo               │
├───────────────────────────────────┤
│ - static instance: mongo          │
├───────────────────────────────────┤
│ + init_app(app)                   │
└───────────────────────────────────┘
      ▲
      │ imports
      │
┌─────┴─────────────────────────────┐
│             app.py                │
├───────────────────────────────────┤
│ - app: Flask                      │
├───────────────────────────────────┤
│ + register_blueprint()            │
└───────────────────────────────────┘
```

### 7.2 Facade Pattern UML

```
┌───────────────────────────┐       ┌───────────────────────────────────────┐
│      Routes               │       │           DatabaseManager              │
├───────────────────────────┤       ├───────────────────────────────────────┤
│                           │       │ - db: mongo.db                         │
├───────────────────────────┤       ├───────────────────────────────────────┤
│ + get_user(user_id)       │──────►│ + create_user(user)                    │
│ + create_user(data)       │       │ + get_user_by_id(user_id)              │
│ + get_meal(meal_id)       │       │ + get_user_by_email(email)             │
│ + create_meal(data)       │       │ + update_user(user)                    │
└───────────────────────────┘       │ + delete_user(user_id)                 │
                                    │ + create_meal(meal)                    │
                                    │ + get_meal_by_id(meal_id)              │
                                    │ + get_meals_by_ids(meal_ids)           │
                                    │ + get_meals_by_query(query, limit)     │
                                    │ + get_random_meals(limit)              │
                                    │ + update_meal(meal)                    │
                                    │ + delete_meal(meal_id)                 │
                                    │ + create_mood_log(user_id, mood, notes)│
                                    │ + get_mood_logs_by_user(user_id, limit)│
                                    │ + create_feedback(feedback)            │
                                    │ + get_user_feedback(user_id, limit)    │
                                    │ + get_meal_feedback(meal_id, limit)    │
                                    └─────────────────┬─────────────────────┘
                                                      │
                                                      │ uses
                                                      ▼
                                    ┌───────────────────────────────────────┐
                                    │             MongoDB                   │
                                    ├───────────────────────────────────────┤
                                    │ - users                               │
                                    │ - meals                               │
                                    │ - mood_logs                           │
                                    │ - feedback                            │
                                    │ - user_preferences                    │
                                    └───────────────────────────────────────┘
```

### 7.3 Factory Method Pattern UML

```
┌───────────────┐         ┌───────────────┐
│  Database     │         │  from_dict()  │
│  Document     │────────►│  Factory      │
└───────────────┘         └───────┬───────┘
                                  │
                                  │
                          ┌───────▼───────┐
                          │  Domain       │
                          │  Object       │
                          └───────────────┘
```

### 7.4 Strategy Pattern UML

```
┌───────────────┐         ┌───────────────┐
│  Client       │         │Recommendation  │
│  Code         │────────►│  Engine       │
└───────────────┘         └───────┬───────┘
                                  │
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
          ┌───────▼───────┐┌──────▼────────┐┌─────▼─────────┐
          │ Mood-based    ││ Personalized  ││ Default       │
          │ Strategy      ││ Strategy      ││ Strategy      │
          └───────────────┘└───────────────┘└───────────────┘
```

### 7.5 Repository Pattern UML

```
┌───────────────┐         ┌───────────────┐
│  Application  │         │ DatabaseManager│
│  Logic        │────────►│  (Repository) │
└───────────────┘         └───────┬───────┘
                                  │
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
          ┌───────▼───────┐┌──────▼────────┐┌─────▼─────────┐
          │ User          ││ Meal          ││ Mood          │
          │ Repository    ││ Repository    ││ Repository    │
          └───────────────┘└───────────────┘└───────────────┘
```

### 7.6 Blueprint Pattern UML (Flask-specific)

```
┌───────────────┐
│  Flask App    │
└───────┬───────┘
        │
        │
┌───────▼───────┐
│  Blueprints   │
└───────┬───────┘
        │
        │
┌───────┴───────────────────────────────────┐
│                                           │
│                                           │
▼                   ▼                       ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ User      │ │ Meal      │ │ Mood      │ │ Admin     │
│ Routes    │ │ Routes    │ │ Routes    │ │ Routes    │
└───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### 7.7 Adapter Pattern UML

```
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  MongoDB      │         │MongoJSONEncoder│         │  JSON         │
│  Data Types   │────────►│   (Adapter)   │────────►│  Response     │
└───────────────┘         └───────────────┘         └───────────────┘
```

### 7.8 Data Transfer Object (DTO) Pattern UML

```
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  Domain       │         │  DTO          │         │  Client       │
│  Object       │────────►│  Object       │────────►│  Code         │
└───────────────┘         └───────────────┘         └───────────────┘
```

### 7.9 Dependency Injection UML

```
┌───────────────┐         ┌───────────────┐
│  Database     │         │Recommendation  │
│  Manager      │────────►│  Engine       │
└───────────────┘         └───────────────┘
       ▲
       │
       │
┌──────┴────────┐
│  Application  │
│  Container    │
└───────────────┘
```

## 7.10 Configuration UML Diagram

```
┌───────────────┐         ┌───────────────┐
│                  Configuration                     │
├───────────────────────────────────────────────────┤
│ - .env file                                       │
│ - app.config                                      │
├───────────────────────────────────────────────────┤
│ + load_dotenv()                                   │
└──────────────────────┬────────────────────────────┘
                       │
                       │ configures
                       ▼
┌───────────────────────────────────────────────────┐
│                  Flask App                        │
├───────────────────────────────────────────────────┤
│ - SECRET_KEY                                      │
│ - MONGO_URI                                       │
│ - DEBUG                                           │
├───────────────────────────────────────────────────┤
│ + __init__()                                      │
└──────────────────────┬────────────────────────────┘
                       │
                       │ uses
                       ▼
┌───────────────────────────────────────────────────┐
│                 Environment                       │
├───────────────────────────────────────────────────┤
│ - SECRET_KEY                                      │
│ - MONGO_URI                                       │
│ - PORT                                            │
│ - HOST                                            │
└───────────────────────────────────────────────────┘
```

### 7.11 Communications UML Diagram

```
┌───────────────┐         ┌───────────────┐
│                  Client                           │
├───────────────────────────────────────────────────┤
│ - Browser                                         │
│ - Mobile App                                      │
├───────────────────────────────────────────────────┤
│ + HTTP Request                                    │
└──────────────────────┬────────────────────────────┘
                       │
                       │ communicates
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────────┐   ┌───────────────────────────┐
│   Blueprints      │   │    MongoJSONEncoder       │
├───────────────────┤   ├───────────────────────────┤
│ - user_bp         │   │                           │
│ - meal_bp         │   ├───────────────────────────┤
│ - mood_bp         │   │ + default(obj)            │
│ - admin_bp        │   └───────────────────────────┘
└────────┬──────────┘
         │
         │ contains
         ▼
┌────────────────────────────────────────┐
│           Route Handlers               │
├────────────────────────────────────────┤
│                                        │
├────────────────────────────────────────┤
│ + create_user()                        │
│ + get_user(user_id)                    │
│ + get_recommendations(user_id, mood)   │────────┐
└──────────────────┬─────────────────────┘        │
                   │                               │
                   │ uses                          │ calls
                   ▼                               │
┌────────────────────────────────────────────────────────────┐
│                  DatabaseManager                           │
├────────────────────────────────────────────────────────────┤
│ - db: mongo.db                                             │
├────────────────────────────────────────────────────────────┤
│ + create_user(user): ObjectId                              │
│ + get_user_by_id(user_id): User                            │
│ + update_user(user): void                                  │
│ + delete_user(user_id): void                               │
│ + create_meal(meal): ObjectId                              │
│ + get_meal_by_id(meal_id): Meal                            │
│ + get_meals_by_query(query, limit): list[Meal]             │
│ + get_random_meals(limit): list[Meal]                      │
│ + create_mood_log(user_id, mood, notes): ObjectId          │
│ + get_mood_logs_by_user(user_id, limit): list[MoodLog]     │
│ + create_feedback(feedback): ObjectId                      │
│ + get_user_preferences(user_id): UserPreferences           │
└───────────────────┬────────────────────────────────────────┘
                    │
                    │ manages
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────────┐   ┌───────────────────────────────────────────┐
│ Domain Models     │   │           RecommendationEngine            │
├───────────────────┤   ├───────────────────────────────────────────┤
│ - User            │   │ - db_manager: DatabaseManager             │
│ - Meal            │   │ - mood_food_mapping: dict                 │
│ - MoodLog         │   ├───────────────────────────────────────────┤
│ - Feedback        │   │ + get_recommendations(user_id, mood, limit)│◄──┘
│ - UserPreferences │   │ + get_personalized_recommendations()      │
└───────────────────┘   │ - _get_default_recommendations()          │
                        └───────────────────────────────────────────┘
```

### 7.12 Controls UML Diagram

```
┌───────────────┐         ┌───────────────┐
│                 Route Handlers                    │
├───────────────────────────────────────────────────┤
│ - request validation                              │
│ - authentication                                  │
│ - authorization                                   │
├───────────────────────────────────────────────────┤
│ + validate_input()                                │
│ + check_auth()                                    │
│ + process_request()                               │
└──────────────────┬────────────────────────────────┘
                   │
                   │ implements
                   ▼
┌───────────────────────────────────────────────────┐
│                 Error Handlers                    │
├───────────────────────────────────────────────────┤
│ - 404 handler                                     │
│ - 500 handler                                     │
│ - validation error handler                        │
├───────────────────────────────────────────────────┤
│ + not_found(error)                                │
│ + server_error(error)                             │
└───────────────────┬────────────────────────────────┘
                   │
                   │ returns
                   ▼
┌───────────────────────────────────────────────────┐
│                 JSON Response                     │
├───────────────────────────────────────────────────┤
│ - status code                                     │
│ - message                                         │
│ - data                                            │
│ - error                                           │
├───────────────────────────────────────────────────┤
│ + jsonify()                                       │
└───────────────────────────────────────────────────┘
```

### 7.13 Complete System UML Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Flask Application                              │
├─────────────────────────────────────────────────────────────────────────┤
│ - app: Flask                                                            │
│ - secret_key: string                                                    │
│ - mongo_uri: string                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ + register_blueprint(blueprint)                                         │
│ + errorhandler(code)                                                    │
└───────────────────┬─────────────────────────────────────────────────────┘
                    │
                    │ contains
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────────┐   ┌───────────────────────────┐
│   Blueprints      │   │    MongoJSONEncoder       │
├───────────────────┤   ├───────────────────────────┤
│ - user_bp         │   │                           │
│ - meal_bp         │   ├───────────────────────────┤
│ - mood_bp         │   │ + default(obj)            │
│ - admin_bp        │   └───────────────────────────┘
└────────┬──────────┘
         │
         │ contains
         ▼
┌────────────────────────────────────────┐
│           Route Handlers               │
├────────────────────────────────────────┤
│                                        │
├────────────────────────────────────────┤
│ + create_user()                        │
│ + get_user(user_id)                    │
│ + get_recommendations(user_id, mood)   │────────┐
└──────────────────┬─────────────────────┘        │
                   │                               │
                   │ uses                          │ calls
                   ▼                               │
┌────────────────────────────────────────────────────────────┐
│                  DatabaseManager                           │
├────────────────────────────────────────────────────────────┤
│ - db: mongo.db                                             │
├────────────────────────────────────────────────────────────┤
│ + create_user(user): ObjectId                              │
│ + get_user_by_id(user_id): User                            │
│ + update_user(user): void                                  │
│ + delete_user(user_id): void                               │
│ + create_meal(meal): ObjectId                              │
│ + get_meal_by_id(meal_id): Meal                            │
│ + get_meals_by_query(query, limit): list[Meal]             │
│ + get_random_meals(limit): list[Meal]                      │
│ + create_mood_log(user_id, mood, notes): ObjectId          │
│ + get_mood_logs_by_user(user_id, limit): list[MoodLog]     │
│ + create_feedback(feedback): ObjectId                      │
│ + get_user_preferences(user_id): UserPreferences           │
└───────────────────┬────────────────────────────────────────┘
                    │
                    │ manages
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────────┐   ┌───────────────────────────────────────────┐
│ Domain Models     │   │           RecommendationEngine            │
├───────────────────┤   ├───────────────────────────────────────────┤
│ - User            │   │ - db_manager: DatabaseManager             │
│ - Meal            │   │ - mood_food_mapping: dict                 │
│ - MoodLog         │   ├───────────────────────────────────────────┤
│ - Feedback        │   │ + get_recommendations(user_id, mood, limit)│◄──┘
│ - UserPreferences │   │ + get_personalized_recommendations()      │
└───────────────────┘   │ - _get_default_recommendations()          │
                        └───────────────────────────────────────────┘
```
