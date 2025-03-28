class RecommendationEngine:
    """
    RecommendationEngine class for processing user mood, preferences, and history 
    to generate personalized meal suggestions.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        # Mapping of moods to food characteristics
        self.mood_food_mapping = {
            "happy": ["comfort food", "celebratory", "colorful", "sweet"],
            "sad": ["comfort food", "warm", "nostalgic", "chocolate"],
            "stressed": ["calming", "easy to prepare", "nutrient-rich", "soothing"],
            "energetic": ["protein-rich", "light", "refreshing", "energizing"],
            "tired": ["energy-boosting", "iron-rich", "simple", "nutritious"],
            "anxious": ["calming", "magnesium-rich", "warm", "comforting"],
            "nostalgic": ["traditional", "homestyle", "childhood favorites"],
            "relaxed": ["balanced", "fresh", "seasonal", "mindful"]
        }
    
    def get_recommendations(self, user_id, mood, limit=10):
        """
        Generate meal recommendations based on user mood and preferences.
        No ML is used as per requirements.
        """
        # Get user preferences
        user_prefs = self.db_manager.get_user_preferences(user_id)
        
        print(f"Getting recommendations for user {user_id}, mood: {mood}")
        print(f"User preferences found: {user_prefs is not None}")
        
        if not user_prefs:
            # Default recommendations if no preferences are set
            print("No user preferences found, getting default recommendations")
            return self._get_default_recommendations(mood, limit)
        
        # Get mood-based food characteristics
        food_characteristics = self.mood_food_mapping.get(mood.lower(), [])
        print(f"Mood food characteristics: {food_characteristics}")
        
        # Query meals based on mood, preferences, and restrictions
        query = {}
        
        # Add mood tags to query
        if food_characteristics:
            query["mood_tags"] = {"$in": food_characteristics}
        
        # Filter by dietary restrictions
        if user_prefs.dietary_restrictions:
            print(f"Filtering by dietary restrictions: {user_prefs.dietary_restrictions}")
            query["nutritional_info.dietary_tags"] = {
                "$nin": user_prefs.dietary_restrictions
            }
        
        # Filter by allergies
        if user_prefs.allergies:
            print(f"Filtering by allergies: {user_prefs.allergies}")
            for allergy in user_prefs.allergies:
                query[f"ingredients"] = {"$not": {"$regex": allergy, "$options": "i"}}
        
        # Preferred cuisines - updated field name from preferred_cuisines to cuisines
        if user_prefs.cuisines:
            print(f"Filtering by preferred cuisines: {user_prefs.cuisines}")
            query["cuisine_type"] = {"$in": user_prefs.cuisines}
        
        print(f"Final query: {query}")
        
        # Get meals from database
        meals = self.db_manager.get_meals_by_query(query, limit)
        print(f"Found {len(meals)} meals matching query")
        
        # If not enough meals found, get some default recommendations
        if len(meals) < limit:
            print(f"Not enough meals found, adding {limit - len(meals)} default recommendations")
            
            # Track meal IDs to avoid duplicates
            existing_meal_ids = {str(meal.meal_id) for meal in meals}
            
            default_meals = self._get_default_recommendations(
                mood, limit - len(meals)
            )
            
            # Only add default meals that aren't already in the results
            for meal in default_meals:
                if str(meal.meal_id) not in existing_meal_ids:
                    meals.append(meal)
                    existing_meal_ids.add(str(meal.meal_id))
        
        # Log this mood entry
        self.db_manager.create_mood_log(user_id, mood)
        
        return meals
    
    def _get_default_recommendations(self, mood, limit=10):
        """Get default recommendations based only on mood"""
        food_characteristics = self.mood_food_mapping.get(mood.lower(), [])
        print(f"Getting default recommendations for mood: {mood}")
        print(f"Food characteristics: {food_characteristics}")
        
        query = {}
        if food_characteristics:
            query["mood_tags"] = {"$in": food_characteristics}
        
        print(f"Default query: {query}")
        meals = self.db_manager.get_meals_by_query(query, limit)
        print(f"Found {len(meals)} meals with default query")
        
        # If still no meals found, return random meals as a fallback
        if not meals:
            print("No meals found with mood tags, returning random meals")
            meals = self.db_manager.get_random_meals(limit)
            print(f"Found {len(meals)} random meals")
        
        return meals
    
    def get_personalized_recommendations(self, user_id, limit=10):
        """
        Get personalized recommendations based on user's previous choices
        and feedback, without considering current mood.
        """
        # Get user's favorite meals
        user_prefs = self.db_manager.get_user_preferences(user_id)
        favorite_meals = []
        
        if user_prefs and user_prefs.favorite_meals:
            favorite_meals = self.db_manager.get_meals_by_ids(user_prefs.favorite_meals)
        
        # Get meals similar to user's favorites
        similar_meals = []
        for meal in favorite_meals:
            if meal.cuisine_type:
                query = {"cuisine_type": meal.cuisine_type}
                similar = self.db_manager.get_meals_by_query(query, 3)
                similar_meals.extend(similar)
        
        # Get user's highly rated meals
        feedback = self.db_manager.get_user_feedback(user_id)
        highly_rated_meal_ids = [f.meal_id for f in feedback if f.rating >= 4]
        highly_rated_meals = self.db_manager.get_meals_by_ids(highly_rated_meal_ids)
        
        # Combine recommendations, remove duplicates, and limit
        recommendations = []
        meal_ids = set()
        
        for meal in similar_meals + highly_rated_meals:
            if meal.meal_id not in meal_ids and len(recommendations) < limit:
                recommendations.append(meal)
                meal_ids.add(meal.meal_id)
        
        # If not enough recommendations, add some random meals
        if len(recommendations) < limit:
            random_meals = self.db_manager.get_random_meals(limit - len(recommendations))
            for meal in random_meals:
                if meal.meal_id not in meal_ids:
                    recommendations.append(meal)
                    meal_ids.add(meal.meal_id)
        
        return recommendations
