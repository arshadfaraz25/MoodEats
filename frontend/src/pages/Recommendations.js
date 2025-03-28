import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { moodAPI, userAPI } from '../services/api';
import MealCard from '../components/MealCard';

const Recommendations = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const moodParam = queryParams.get('mood');
  
  const [recommendations, setRecommendations] = useState([]);
  const [favorites, setFavorites] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [currentMood, setCurrentMood] = useState(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [filters, setFilters] = useState({
    cuisine: '',
    dietary: [],
    mealType: '',
    calorieRange: [0, 1000]
  });
  const [availableMoods, setAvailableMoods] = useState([]);
  
  // Fetch available moods for reference
  useEffect(() => {
    const fetchMoods = async () => {
      try {
        const response = await moodAPI.getAvailableMoods();
        setAvailableMoods(response.data);
        
        // Set current mood from the list
        if (moodParam) {
          const foundMood = response.data.find(mood => mood.id === moodParam);
          if (foundMood) {
            setCurrentMood(foundMood);
          }
        }
      } catch (error) {
        console.error('Error fetching moods:', error);
      }
    };
    
    fetchMoods();
  }, [moodParam]);
  
  // Fetch recommendations based on mood
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!moodParam) return;
      
      setLoading(true);
      try {
        const response = await moodAPI.getRecommendations(moodParam, 12);
        setRecommendations(response.data);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRecommendations();
  }, [moodParam]);
  
  // Fetch user favorites
  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        const response = await userAPI.getFavorites();
        const favSet = new Set(response.data.map(meal => meal._id));
        setFavorites(favSet);
      } catch (error) {
        console.error('Error fetching favorites:', error);
      }
    };
    
    fetchFavorites();
  }, []);
  
  const handleFavoriteToggle = (mealId, isFavorite) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (isFavorite) {
        newFavorites.add(mealId);
      } else {
        newFavorites.delete(mealId);
      }
      return newFavorites;
    });
  };
  
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const toggleDietaryFilter = (tag) => {
    setFilters(prev => {
      const newDietary = [...prev.dietary];
      if (newDietary.includes(tag)) {
        return {
          ...prev,
          dietary: newDietary.filter(t => t !== tag)
        };
      } else {
        return {
          ...prev,
          dietary: [...newDietary, tag]
        };
      }
    });
  };
  
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
  
  const filteredRecommendations = applyFilters(recommendations);
  
  // Get unique cuisine types and meal types for filters
  const cuisineTypes = [...new Set(recommendations.map(meal => meal.cuisine_type).filter(Boolean))];
  const mealTypes = [...new Set(recommendations.map(meal => meal.meal_type).filter(Boolean))];
  const dietaryTags = [...new Set(
    recommendations
      .filter(meal => meal.nutritional_info && meal.nutritional_info.dietary_tags)
      .flatMap(meal => meal.nutritional_info.dietary_tags)
  )];
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
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
          <p className="text-gray-600 mt-2">
            {currentMood ? (
              `Meals specially selected for when you're feeling ${currentMood.name.toLowerCase()}`
            ) : (
              'Personalized meal suggestions based on your preferences'
            )}
          </p>
        </div>
        
        <div className="mt-4 md:mt-0">
          <button 
            onClick={() => setFilterOpen(!filterOpen)}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clipRule="evenodd" />
            </svg>
            Filters
          </button>
        </div>
      </div>
      
      {/* Filter modal - inspired by Airbnb's filter modal */}
      {filterOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75" onClick={() => setFilterOpen(false)}></div>
            </div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Filters</h3>
                    
                    {/* Cuisine Type */}
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Cuisine Type</label>
                      <select
                        className="input-field"
                        value={filters.cuisine}
                        onChange={(e) => handleFilterChange('cuisine', e.target.value)}
                      >
                        <option value="">Any Cuisine</option>
                        {cuisineTypes.map(cuisine => (
                          <option key={cuisine} value={cuisine}>{cuisine}</option>
                        ))}
                      </select>
                    </div>
                    
                    {/* Meal Type */}
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Meal Type</label>
                      <select
                        className="input-field"
                        value={filters.mealType}
                        onChange={(e) => handleFilterChange('mealType', e.target.value)}
                      >
                        <option value="">Any Type</option>
                        {mealTypes.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    
                    {/* Dietary Tags */}
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Dietary Preferences</label>
                      <div className="flex flex-wrap gap-2">
                        {dietaryTags.map(tag => (
                          <button
                            key={tag}
                            onClick={() => toggleDietaryFilter(tag)}
                            className={`px-3 py-1 rounded-full text-sm ${
                              filters.dietary.includes(tag)
                                ? 'bg-brand-primary text-white'
                                : 'bg-gray-200 text-gray-700'
                            }`}
                          >
                            {tag}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    {/* Calorie Range */}
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Calorie Range: {filters.calorieRange[0]} - {filters.calorieRange[1]}
                      </label>
                      <div className="flex items-center gap-4">
                        <input
                          type="range"
                          min="0"
                          max="1000"
                          step="50"
                          value={filters.calorieRange[0]}
                          onChange={(e) => handleFilterChange('calorieRange', [parseInt(e.target.value), filters.calorieRange[1]])}
                          className="w-full"
                        />
                        <input
                          type="range"
                          min="0"
                          max="1000"
                          step="50"
                          value={filters.calorieRange[1]}
                          onChange={(e) => handleFilterChange('calorieRange', [filters.calorieRange[0], parseInt(e.target.value)])}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-brand-primary text-base font-medium text-white hover:bg-opacity-90 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setFilterOpen(false)}
                >
                  Apply Filters
                </button>
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => {
                    setFilters({
                      cuisine: '',
                      dietary: [],
                      mealType: '',
                      calorieRange: [0, 1000]
                    });
                  }}
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Results section */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
        </div>
      ) : filteredRecommendations.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRecommendations.map(meal => (
            <MealCard 
              key={meal._id} 
              meal={meal} 
              isFavorite={favorites.has(meal._id)}
              onFavoriteToggle={handleFavoriteToggle}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No meals match your filters</h3>
          <p className="mt-2 text-gray-500">Try adjusting your filters or selecting a different mood.</p>
          <button
            onClick={() => {
              setFilters({
                cuisine: '',
                dietary: [],
                mealType: '',
                calorieRange: [0, 1000]
              });
            }}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-brand-primary hover:bg-opacity-90 focus:outline-none"
          >
            Clear Filters
          </button>
        </div>
      )}
      
      {/* Change mood section */}
      <div className="mt-12 bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Try a Different Mood</h2>
        <p className="text-gray-600 mb-6">
          Your mood can change throughout the day. Select a different mood to get new recommendations.
        </p>
        
        <div className="flex flex-wrap gap-3">
          {availableMoods.map(mood => (
            <Link
              key={mood.id}
              to={`/recommendations?mood=${mood.id}`}
              className={`flex items-center px-4 py-2 rounded-full ${
                currentMood && currentMood.id === mood.id
                  ? 'bg-brand-primary text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              <span className="mr-2">{mood.emoji}</span>
              {mood.name}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Recommendations;
