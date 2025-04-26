# JavaScript Control Structures in MoodEats

This document provides real examples of JavaScript control structures used in the MoodEats frontend codebase. These examples can be incorporated into the main implementation report to provide more concrete documentation of the actual coding patterns used in the project.

## If Statements

```javascript
// Basic if-else statement
if (condition) {
  statement1;
  statement2;
} else if (anotherCondition) {
  statement3;
} else {
  statement4;
}

// Real example from MealCard.js - Conditional logic for favorite toggling
const handleFavoriteToggle = async (e) => {
  e.preventDefault();
  e.stopPropagation();
  
  if (!isAuthenticated) {
    console.log('User not authenticated, cannot toggle favorite');
    return;
  }
  
  try {
    if (isFavorite) {
      await userAPI.removeFavorite(meal._id);
    } else {
      await userAPI.addFavorite(meal._id);
    }
    
    if (onFavoriteToggle) {
      onFavoriteToggle(meal._id, !isFavorite);
    }
  } catch (error) {
    console.error('Error toggling favorite:', error);
  }
};
```

## Ternary Operators for Conditional Rendering

```javascript
// Basic ternary syntax
condition ? expressionIfTrue : expressionIfFalse;

// Real example from Recommendations.js - Conditional rendering based on mood
<h1 className="text-3xl font-bold text-brand-dark">
  {currentMood ? (
    <>
      <span className="mr-2">{currentMood.emoji}</span>
      {currentMood.name} Mood Recommendations
    </>
  ) : (
    'Meal Recommendations'
  )}
</h1>
```

## Logical AND for Conditional Rendering

```javascript
// Basic logical AND for conditional rendering
{condition && <ComponentToRender />}

// Real example from AdminAnalytics.js - Conditional rendering of meal data
{data.popular_meals && data.popular_meals.length > 0 ? (
  data.popular_meals.map((meal, index) => (
    <tr key={meal._id}>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {index + 1}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {/* Meal details */}
      </td>
    </tr>
  ))
) : (
  <tr>
    <td colSpan="5" className="text-center py-4 text-gray-500">
      No data available
    </td>
  </tr>
)}
```

## Switch Statements

```javascript
// Basic switch statement
switch (expression) {
  case value1:
    statement1;
    break;
  case value2:
    statement2;
    break;
  default:
    defaultStatement;
}

// Real example from AdminAnalytics.js - Rendering different analytics based on type
const renderAnalyticsContent = () => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4">
        {/* Error display */}
      </div>
    );
  }
  
  switch (analyticsType) {
    case 'user':
      return renderUserAnalytics();
    case 'meal':
      return renderMealAnalytics();
    case 'mood':
      return renderMoodAnalytics();
    default:
      return renderUserAnalytics();
  }
};
```

## For Loops and Array Methods

```javascript
// Traditional for loop
for (let i = 0; i < array.length; i++) {
  processItem(array[i]);
}

// Modern array methods
// Real example from Recommendations.js - Filtering meals based on criteria
const applyFilters = (meals) => {
  return meals.filter(meal => {
    // Filter by cuisine
    if (filters.cuisine && meal.cuisine_type !== filters.cuisine) {
      return false;
    }
    
    // Filter by meal type
    if (filters.mealType && meal.meal_type !== filters.mealType) {
      return false;
    }
    
    // Filter by dietary restrictions
    if (filters.dietary.length > 0 && meal.nutritional_info && meal.nutritional_info.dietary_tags) {
      const hasTags = filters.dietary.every(tag => 
        meal.nutritional_info.dietary_tags.includes(tag)
      );
      if (!hasTags) return false;
    }
    
    // Filter by calorie range
    if (meal.nutritional_info && meal.nutritional_info.calories) {
      const calories = meal.nutritional_info.calories;
      if (calories < filters.calorieRange[0] || calories > filters.calorieRange[1]) {
        return false;
      }
    }
    
    return true;
  });
};

// Real example from Dashboard.js - Using map for rendering mood items
{recentMoods.map((mood, index) => {
  const moodInfo = availableMoods.find(m => m.id === mood.mood) || { name: mood.mood, emoji: '😐' };
  return (
    <div key={index} className="bg-white rounded-lg shadow-sm p-4 text-center">
      <div className="text-4xl mb-2">{moodInfo.emoji}</div>
      <div className="font-medium">{moodInfo.name}</div>
      <p className="text-xs text-gray-500 mt-1">
        {new Date(mood.timestamp).toLocaleDateString()}
      </p>
      <Link
        to={`/recommendations?mood=${mood.mood}`}
        className="text-sm text-brand-primary hover:underline mt-2 inline-block"
      >
        View meals
      </Link>
    </div>
  );
})}
```

## Try/Catch for Error Handling

```javascript
// Basic try/catch
try {
  riskyOperation();
} catch (error) {
  handleError(error);
} finally {
  cleanup();
}

// Real example from Favorites.js - Fetching favorites with error handling
const fetchFavorites = async () => {
  try {
    // First check if user is authenticated
    const isAuth = await checkSession();
    if (!isAuth) return;
    
    console.log('Fetching favorites...');
    const response = await userAPI.getFavorites();
    
    if (response.data && Array.isArray(response.data)) {
      setFavorites(response.data);
      setError(null);
    } else {
      console.error('Unexpected response format:', response.data);
      setFavorites([]);
      setError('Received invalid data format from server');
    }
  } catch (error) {
    console.error('Error fetching favorites:', error);
    
    if (error.response && error.response.status === 401) {
      setIsAuthenticated(false);
      setError('Please log in to view your favorites');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setError('Failed to load your favorites. Please try again later.');
    }
  } finally {
    setLoading(false);
  }
};
```

## Async/Await Pattern

```javascript
// Basic async/await pattern
const asyncFunction = async () => {
  try {
    const result = await someAsyncOperation();
    processResult(result);
  } catch (error) {
    handleError(error);
  }
};

// Real example from MoodSelection.js - Submitting mood selection
const handleSubmit = async () => {
  if (!selectedMood || submitting) return;

  try {
    setSubmitting(true);
    // Log the mood
    await moodAPI.logMood({ mood: selectedMood.id, notes: `Selected from mood selection page` });
    
    // Navigate to recommendations with the selected mood
    navigate(`/recommendations?mood=${selectedMood.id}`);
  } catch (error) {
    console.error('Error logging mood:', error);
    setSubmitting(false);
  }
};
```

## State-Based Conditional Rendering

```javascript
// Real example from Profile.js - Conditional rendering based on loading state
if (loading) {
  return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
    </div>
  );
}
```

## Key JavaScript Control Flow Patterns in MoodEats

In JavaScript and React code, the project leverages modern ES6+ features for more expressive control flow:

1. **Functional Approaches**: Array methods like `map()`, `filter()`, and `reduce()` are preferred over traditional loops when transforming data, particularly in React components that render lists of items. The MoodHistory component, for example, uses `map()` to transform mood data into UI elements.

2. **Conditional Rendering**: React components use ternary operators and logical AND (`&&`) for concise conditional rendering, with more complex conditions extracted into descriptive helper functions. This is evident in the Recommendations component where UI elements are conditionally displayed based on the current mood.

3. **Async/Await**: Asynchronous operations use async/await syntax rather than promise chains for improved readability, with proper error handling via try/catch blocks. The MealDetails component demonstrates this pattern when fetching meal data and handling user interactions.

4. **State Management**: React's useState and useEffect hooks control component lifecycle and state transitions in a declarative rather than imperative style. The Dashboard component uses multiple state variables to track loading states, user data, and UI interactions.

5. **Early Returns**: Functions often use early returns to handle edge cases or validation, reducing nesting and improving readability. This pattern is visible in the MealCard component's event handlers.

6. **Destructuring**: Object and array destructuring is used extensively to extract needed values from complex data structures, making code more concise and readable.
