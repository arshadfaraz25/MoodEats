### Comments
Comments are used to explain complex logic, document functions, and provide context for code sections.

Effective commenting is a cornerstone of the MoodEats development process. The project employs a comprehensive commenting strategy that goes beyond simply explaining what the code does—it focuses on explaining why certain implementation decisions were made, particularly for complex algorithms like the mood-based recommendation engine.

Comments in MoodEats serve multiple purposes:
1. **Documentation**: Explaining the purpose and usage of functions, classes, and modules
2. **Clarification**: Making complex logic more understandable
3. **Maintenance**: Highlighting areas that may need future attention or optimization
4. **Collaboration**: Facilitating teamwork by communicating intent to other developers
5. **API Description**: Detailing parameter requirements and return values

#### Python Comments:
- Docstrings for modules, classes, and functions using triple quotes
- Single-line comments using `#` for inline explanations
- TODO comments for future improvements

##### Module-Level Docstrings
```python
"""
Module: recommendation_engine.py

This module contains the core recommendation algorithm for MoodEats.
It provides functions to match user moods with appropriate meal suggestions
based on mood-food correlations, user preferences, and dietary restrictions.

Dependencies:
- database_manager.py: For database access
- user_preferences.py: For user preference models
- meal.py: For meal data models
"""
```

##### Class Docstrings
```python
class DatabaseManager:
    """
    Handles all database operations for the MoodEats application.
    
    This class provides an abstraction layer between the application and
    the MongoDB database. It handles connection management, CRUD operations,
    and query optimization for all collections.
    
    Attributes:
        client: MongoDB client connection
        db: Database instance
        collections: Dictionary of collection references
    """
```

##### Function Docstrings
```python
def get_recommendations(self, user_id, mood, limit=10):
    """
    Generate personalized meal recommendations based on user mood and preferences.
    
    This function is the core of the recommendation engine. It combines mood-food
    mappings with user dietary restrictions and preferences to create a personalized
    list of meal recommendations that may help improve or maintain the user's
    emotional state.
    
    Args:
        user_id (str): The ID of the user requesting recommendations
        mood (str): The current mood of the user (e.g., "happy", "sad", "stressed")
        limit (int, optional): Maximum number of recommendations to return. Defaults to 10.
        
    Returns:
        list: Ordered list of meal recommendations sorted by relevance score
        
    Raises:
        ValueError: If the mood is not recognized
        DatabaseError: If there's an issue retrieving user preferences
    """
    # Get user preferences including dietary restrictions
    user_prefs = self.db_manager.get_user_preferences(user_id)
    
    # Validate the mood input
    if mood.lower() not in self.valid_moods:
        raise ValueError(f"Unrecognized mood: {mood}")
    
    # Get mood-based food characteristics
    # These are the types of foods that may positively affect the given mood
    food_characteristics = self.mood_food_mapping.get(mood.lower(), [])
    
    # TODO: Implement machine learning model for better recommendations
    # Current implementation uses a rule-based approach, but future versions
    # will incorporate user feedback and machine learning for improved accuracy
```

##### Inline Comments
```python
# Convert ObjectId to string for JSON serialization
meal["_id"] = str(meal["_id"])

# Skip meals that contain allergens the user is sensitive to
if any(allergen in meal["ingredients"] for allergen in user_prefs.allergies):
    continue

# Calculate relevance score based on mood match and user preferences
# Higher scores indicate better matches for the current mood
relevance_score = self._calculate_relevance(meal, food_characteristics, user_prefs)
```

##### Block Comments for Complex Logic
```python
def _calculate_relevance(self, meal, characteristics, user_prefs):
    """Calculate relevance score for a meal based on mood and preferences."""
    base_score = 0
    
    # -----------------------------------------------------------------------
    # Mood matching algorithm:
    # 1. Start with a base score of 0
    # 2. Add points for each matching mood tag (weighted by importance)
    # 3. Add bonus points for exact matches to the primary mood
    # 4. Add points for matching user's preferred cuisines and ingredients
    # 5. Subtract points for ingredients the user has rated poorly in the past
    # -----------------------------------------------------------------------
    
    # Step 2: Add points for matching mood tags
    for char in characteristics:
        if char in meal["mood_tags"]:
            # Primary characteristics are weighted more heavily
            weight = 2 if char in self.primary_characteristics else 1
            base_score += weight * self.tag_importance[char]
    
    # Additional scoring logic...
    
    return base_score
```

#### JavaScript Comments:

##### Component Documentation
```javascript
/**
 * MealCard Component
 * 
 * Displays a meal card with image, title, description, and action buttons.
 * Used in multiple views including recommendations, search results, and favorites.
 * 
 * @component
 * @example
 * // Basic usage
 * <MealCard 
 *   meal={mealObject} 
 *   onFavorite={handleFavorite} 
 * />
 * 
 * // With all options
 * <MealCard 
 *   meal={mealObject} 
 *   onFavorite={handleFavorite}
 *   showDetails={true}
 *   isRecommended={true}
 *   highlightReason="Perfect for your current mood"
 * />
 */
const MealCard = ({ meal, onFavorite, showDetails = true, isRecommended = false, highlightReason = "" }) => {
  const { name, description, image, prepTime, cookTime, tags } = meal;
  
  // Component implementation
};
```

##### Function Documentation
```javascript
/**
 * Handles user logout and redirects to home page.
 * 
 * This function performs the following operations:
 * 1. Calls the logout API endpoint to invalidate the server session
 * 2. Clears the authentication token from local storage
 * 3. Updates the authentication context state
 * 4. Redirects the user to the home page
 * 
 * @async
 * @function handleLogout
 * @returns {Promise<void>}
 */
const handleLogout = async () => {
  // Show loading indicator during logout process
  setIsLoading(true);
  
  try {
    // Call API to invalidate server session
    await logout();
    
    // Redirect to home page after successful logout
    navigate('/');
  } catch (error) {
    // Display error notification if logout fails
    setErrorMessage("Logout failed. Please try again.");
    console.error("Logout error:", error);
  } finally {
    setIsLoading(false);
  }
};
```

##### Inline Comments
```javascript
// Use memoization to prevent unnecessary re-renders
const filteredMeals = useMemo(() => {
  return meals.filter(meal => meal.tags.includes(selectedTag));
}, [meals, selectedTag]);

// Format date to local string representation
const formattedDate = new Date(timestamp).toLocaleDateString();

// Prevent default form submission behavior
event.preventDefault();
```

##### Section Comments
```javascript
// =========================================
// Authentication State Management
// =========================================
const [user, setUser] = useState(null);
const [isAuthenticated, setIsAuthenticated] = useState(false);
const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));
const [loading, setLoading] = useState(true);

// =========================================
// API Communication Functions
// =========================================
const fetchUserProfile = async () => {
  // Implementation...
};

const updateUserPreferences = async (preferences) => {
  // Implementation...
};
```

##### Complex Logic Comments
```javascript
/**
 * Calculates the recommended portion size based on user profile and preferences.
 * 
 * The algorithm considers:
 * - User's caloric needs (based on age, weight, height, activity level)
 * - Dietary goals (weight loss, maintenance, gain)
 * - Meal type (breakfast, lunch, dinner, snack)
 * - Nutritional density of the meal
 * 
 * @param {Object} user - User profile information
 * @param {Object} meal - Meal nutritional information
 * @param {string} mealType - Type of meal (breakfast, lunch, dinner, snack)
 * @returns {Object} Recommended portion size and nutritional breakdown
 */
function calculatePortionSize(user, meal, mealType) {
  // Implementation details...
}
```

This multi-level commenting approach ensures that code is well-documented at various levels of detail, making it accessible to developers with different levels of familiarity with the codebase. The consistent comment formatting also facilitates automated documentation generation and code navigation tools.
