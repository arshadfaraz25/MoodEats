import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';

const AdminMeals = () => {
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  
  // Form state for new/edit meal
  const [mealForm, setMealForm] = useState({
    name: '',
    description: '',
    ingredients: [],
    recipe_steps: [],
    image_url: '',
    prep_time: '',
    cook_time: '',
    cuisine_type: '',
    meal_type: '',
    mood_tags: [],
    nutritional_info: {
      calories: '',
      protein: '',
      carbs: '',
      fat: '',
      dietary_tags: []
    }
  });
  
  // Options for dropdowns
  const cuisineOptions = [
    'Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 
    'Thai', 'French', 'Mediterranean', 'American', 'Middle Eastern'
  ];
  
  const mealTypeOptions = [
    'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert', 'Appetizer'
  ];
  
  const moodTagOptions = [
    'Happy', 'Sad', 'Stressed', 'Relaxed', 'Energetic', 
    'Tired', 'Hungry', 'Bored', 'Sick', 'Celebratory'
  ];
  
  const dietaryTagOptions = [
    'Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 
    'Keto', 'Paleo', 'Low-Carb', 'Low-Fat', 'Pescatarian'
  ];
  
  useEffect(() => {
    const fetchMeals = async () => {
      try {
        setLoading(true);
        const response = await adminAPI.getMeals();
        setMeals(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching meals:', err);
        setError('Failed to load meals. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchMeals();
  }, []);
  
  const handleDeleteMeal = async (mealId) => {
    if (!window.confirm('Are you sure you want to delete this meal? This action cannot be undone.')) {
      return;
    }
    
    try {
      await adminAPI.deleteMeal(mealId);
      setMeals(meals.filter(meal => meal._id !== mealId));
    } catch (err) {
      console.error('Error deleting meal:', err);
      setError('Failed to delete meal. Please try again later.');
    }
  };
  
  const handleEditMeal = (meal) => {
    setSelectedMeal(meal);
    setMealForm({
      name: meal.name || '',
      description: meal.description || '',
      ingredients: meal.ingredients || [],
      recipe_steps: meal.recipe_steps || [],
      image_url: meal.image_url || '',
      prep_time: meal.prep_time || '',
      cook_time: meal.cook_time || '',
      cuisine_type: meal.cuisine_type || '',
      meal_type: meal.meal_type || '',
      mood_tags: meal.mood_tags || [],
      nutritional_info: {
        calories: meal.nutritional_info?.calories || '',
        protein: meal.nutritional_info?.protein || '',
        carbs: meal.nutritional_info?.carbs || '',
        fat: meal.nutritional_info?.fat || '',
        dietary_tags: meal.nutritional_info?.dietary_tags || []
      }
    });
    setIsEditing(true);
  };
  
  const handleCreateMeal = () => {
    setMealForm({
      name: '',
      description: '',
      ingredients: [],
      recipe_steps: [],
      image_url: '',
      prep_time: '',
      cook_time: '',
      cuisine_type: '',
      meal_type: '',
      mood_tags: [],
      nutritional_info: {
        calories: '',
        protein: '',
        carbs: '',
        fat: '',
        dietary_tags: []
      }
    });
    setIsCreating(true);
  };
  
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    if (name.includes('nutritional_info.')) {
      const nutritionalField = name.split('.')[1];
      setMealForm(prev => ({
        ...prev,
        nutritional_info: {
          ...prev.nutritional_info,
          [nutritionalField]: value
        }
      }));
    } else {
      setMealForm(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  const handleArrayChange = (e) => {
    const { name, value } = e.target;
    setMealForm(prev => ({
      ...prev,
      [name]: value.split('\n').filter(item => item.trim() !== '')
    }));
  };
  
  const handleCheckboxChange = (field, value) => {
    if (field === 'dietary_tags') {
      setMealForm(prev => {
        const currentTags = [...prev.nutritional_info.dietary_tags];
        if (currentTags.includes(value)) {
          return {
            ...prev,
            nutritional_info: {
              ...prev.nutritional_info,
              dietary_tags: currentTags.filter(tag => tag !== value)
            }
          };
        } else {
          return {
            ...prev,
            nutritional_info: {
              ...prev.nutritional_info,
              dietary_tags: [...currentTags, value]
            }
          };
        }
      });
    } else {
      setMealForm(prev => {
        const currentTags = [...prev[field]];
        if (currentTags.includes(value)) {
          return {
            ...prev,
            [field]: currentTags.filter(tag => tag !== value)
          };
        } else {
          return {
            ...prev,
            [field]: [...currentTags, value]
          };
        }
      });
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (isEditing) {
        await adminAPI.updateMeal(selectedMeal._id, mealForm);
        
        // Update meals list
        setMeals(meals.map(meal => 
          meal._id === selectedMeal._id 
            ? { ...meal, ...mealForm } 
            : meal
        ));
        
        setIsEditing(false);
      } else {
        const response = await adminAPI.createMeal(mealForm);
        
        // Add new meal to list
        setMeals([...meals, { ...mealForm, _id: response.data.meal_id }]);
        
        setIsCreating(false);
      }
      
      setSelectedMeal(null);
      setError(null);
    } catch (err) {
      console.error('Error saving meal:', err);
      setError('Failed to save meal. Please try again later.');
    }
  };
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
      </div>
    );
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-brand-dark">Meal Management</h1>
        <button 
          onClick={handleCreateMeal}
          className="btn-primary"
        >
          Add New Meal
        </button>
      </div>
      
      {error && (
        <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {(isEditing || isCreating) ? (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">
            {isEditing ? 'Edit Meal' : 'Create New Meal'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Meal Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={mealForm.name}
                  onChange={handleFormChange}
                  className="input-field mt-1"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="image_url" className="block text-sm font-medium text-gray-700">
                  Image URL
                </label>
                <input
                  type="text"
                  id="image_url"
                  name="image_url"
                  value={mealForm.image_url}
                  onChange={handleFormChange}
                  className="input-field mt-1"
                  placeholder="https://example.com/image.jpg"
                />
              </div>
              
              <div>
                <label htmlFor="cuisine_type" className="block text-sm font-medium text-gray-700">
                  Cuisine Type
                </label>
                <select
                  id="cuisine_type"
                  name="cuisine_type"
                  value={mealForm.cuisine_type}
                  onChange={handleFormChange}
                  className="input-field mt-1"
                >
                  <option value="">Select Cuisine</option>
                  {cuisineOptions.map(cuisine => (
                    <option key={cuisine} value={cuisine}>{cuisine}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="meal_type" className="block text-sm font-medium text-gray-700">
                  Meal Type
                </label>
                <select
                  id="meal_type"
                  name="meal_type"
                  value={mealForm.meal_type}
                  onChange={handleFormChange}
                  className="input-field mt-1"
                >
                  <option value="">Select Meal Type</option>
                  {mealTypeOptions.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="prep_time" className="block text-sm font-medium text-gray-700">
                  Prep Time (minutes)
                </label>
                <input
                  type="number"
                  id="prep_time"
                  name="prep_time"
                  value={mealForm.prep_time}
                  onChange={handleFormChange}
                  className="input-field mt-1"
                  min="0"
                />
              </div>
              
              <div>
                <label htmlFor="cook_time" className="block text-sm font-medium text-gray-700">
                  Cook Time (minutes)
                </label>
                <input
                  type="number"
                  id="cook_time"
                  name="cook_time"
                  value={mealForm.cook_time}
                  onChange={handleFormChange}
                  className="input-field mt-1"
                  min="0"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={mealForm.description}
                onChange={handleFormChange}
                rows="3"
                className="input-field mt-1"
              ></textarea>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="ingredients" className="block text-sm font-medium text-gray-700">
                  Ingredients (one per line)
                </label>
                <textarea
                  id="ingredients"
                  name="ingredients"
                  value={mealForm.ingredients.join('\n')}
                  onChange={handleArrayChange}
                  rows="5"
                  className="input-field mt-1"
                ></textarea>
              </div>
              
              <div>
                <label htmlFor="recipe_steps" className="block text-sm font-medium text-gray-700">
                  Recipe Steps (one per line)
                </label>
                <textarea
                  id="recipe_steps"
                  name="recipe_steps"
                  value={mealForm.recipe_steps.join('\n')}
                  onChange={handleArrayChange}
                  rows="5"
                  className="input-field mt-1"
                ></textarea>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mood Tags
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {moodTagOptions.map(tag => (
                  <div key={tag} className="flex items-center">
                    <input
                      id={`mood-${tag}`}
                      type="checkbox"
                      checked={mealForm.mood_tags.includes(tag)}
                      onChange={() => handleCheckboxChange('mood_tags', tag)}
                      className="h-4 w-4 text-brand-primary focus:ring-brand-primary border-gray-300 rounded"
                    />
                    <label htmlFor={`mood-${tag}`} className="ml-2 block text-sm text-gray-900">
                      {tag}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Nutritional Information</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div>
                  <label htmlFor="calories" className="block text-sm font-medium text-gray-700">
                    Calories
                  </label>
                  <input
                    type="number"
                    id="calories"
                    name="nutritional_info.calories"
                    value={mealForm.nutritional_info.calories}
                    onChange={handleFormChange}
                    className="input-field mt-1"
                    min="0"
                  />
                </div>
                
                <div>
                  <label htmlFor="protein" className="block text-sm font-medium text-gray-700">
                    Protein (g)
                  </label>
                  <input
                    type="number"
                    id="protein"
                    name="nutritional_info.protein"
                    value={mealForm.nutritional_info.protein}
                    onChange={handleFormChange}
                    className="input-field mt-1"
                    min="0"
                  />
                </div>
                
                <div>
                  <label htmlFor="carbs" className="block text-sm font-medium text-gray-700">
                    Carbs (g)
                  </label>
                  <input
                    type="number"
                    id="carbs"
                    name="nutritional_info.carbs"
                    value={mealForm.nutritional_info.carbs}
                    onChange={handleFormChange}
                    className="input-field mt-1"
                    min="0"
                  />
                </div>
                
                <div>
                  <label htmlFor="fat" className="block text-sm font-medium text-gray-700">
                    Fat (g)
                  </label>
                  <input
                    type="number"
                    id="fat"
                    name="nutritional_info.fat"
                    value={mealForm.nutritional_info.fat}
                    onChange={handleFormChange}
                    className="input-field mt-1"
                    min="0"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dietary Tags
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {dietaryTagOptions.map(tag => (
                    <div key={tag} className="flex items-center">
                      <input
                        id={`diet-${tag}`}
                        type="checkbox"
                        checked={mealForm.nutritional_info.dietary_tags.includes(tag)}
                        onChange={() => handleCheckboxChange('dietary_tags', tag)}
                        className="h-4 w-4 text-brand-primary focus:ring-brand-primary border-gray-300 rounded"
                      />
                      <label htmlFor={`diet-${tag}`} className="ml-2 block text-sm text-gray-900">
                        {tag}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  setIsCreating(false);
                  setSelectedMeal(null);
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
              >
                {isEditing ? 'Update Meal' : 'Create Meal'}
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meal
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cuisine
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mood Tags
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {meals.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">
                      No meals found
                    </td>
                  </tr>
                ) : (
                  meals.map((meal) => (
                    <tr key={meal._id}>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0">
                            <img 
                              className="h-10 w-10 rounded-full object-cover" 
                              src={meal.image_url || 'https://via.placeholder.com/40?text=Meal'} 
                              alt={meal.name} 
                            />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {meal.name}
                            </div>
                            {meal.nutritional_info && (
                              <div className="text-xs text-gray-500">
                                {meal.nutritional_info.calories} cal
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {meal.cuisine_type || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {meal.meal_type || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <div className="flex flex-wrap gap-1">
                          {meal.mood_tags && meal.mood_tags.slice(0, 3).map((tag, index) => (
                            <span 
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-primary bg-opacity-10 text-brand-primary"
                            >
                              {tag}
                            </span>
                          ))}
                          {meal.mood_tags && meal.mood_tags.length > 3 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                              +{meal.mood_tags.length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                          onClick={() => handleEditMeal(meal)} 
                          className="text-brand-primary hover:text-brand-dark mr-4"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => handleDeleteMeal(meal._id)} 
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMeals;
