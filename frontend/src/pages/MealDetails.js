import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { mealAPI, userAPI } from '../services/api';

const MealDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [meal, setMeal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);

  useEffect(() => {
    const fetchMeal = async () => {
      try {
        const response = await mealAPI.getMeal(id);
        setMeal(response.data);
        
        // Check if this meal is in user's favorites
        const favoritesResponse = await userAPI.getFavorites();
        const favorites = favoritesResponse.data;
        setIsFavorite(favorites.some(fav => fav._id === id));
      } catch (error) {
        console.error('Error fetching meal details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMeal();
  }, [id]);

  const handleFavoriteToggle = async () => {
    try {
      if (isFavorite) {
        await userAPI.removeFavorite(id);
      } else {
        await userAPI.addFavorite(id);
      }
      setIsFavorite(!isFavorite);
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (rating === 0) return;

    setSubmittingFeedback(true);
    try {
      await mealAPI.addFeedback(id, {
        rating,
        comment
      });
      setFeedbackSuccess(true);
      setRating(0);
      setComment('');
      
      // Refresh meal data to show updated feedback
      const response = await mealAPI.getMeal(id);
      setMeal(response.data);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
      </div>
    );
  }

  if (!meal) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Meal not found</h2>
        <p className="mt-2 text-gray-600">The meal you're looking for doesn't exist or has been removed.</p>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-brand-primary hover:bg-opacity-90 focus:outline-none"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Back button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center text-brand-primary hover:underline mb-6"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
        </svg>
        Back to recommendations
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left column - Image and details */}
        <div>
          <div className="relative">
            <img 
              src={meal.image_url || 'https://via.placeholder.com/600x400?text=No+Image'} 
              alt={meal.name}
              className="w-full h-96 object-cover rounded-xl"
            />
            <button
              onClick={handleFavoriteToggle}
              className="absolute top-4 right-4 p-3 rounded-full bg-white shadow-md hover:scale-110 transition-transform"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-6 w-6" 
                fill={isFavorite ? "currentColor" : "none"} 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                strokeWidth={isFavorite ? "0" : "2"}
                className={isFavorite ? "text-brand-primary h-6 w-6" : "text-gray-400 h-6 w-6"}
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" 
                />
              </svg>
            </button>
          </div>

          <div className="mt-6">
            <div className="flex flex-wrap gap-2 mb-4">
              {meal.mood_tags && meal.mood_tags.map((tag, index) => (
                <span 
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-brand-primary bg-opacity-10 text-brand-primary"
                >
                  {tag}
                </span>
              ))}
              {meal.nutritional_info && meal.nutritional_info.dietary_tags && 
                meal.nutritional_info.dietary_tags.map((tag, index) => (
                  <span 
                    key={`diet-${index}`}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-brand-secondary bg-opacity-10 text-brand-secondary"
                  >
                    {tag}
                  </span>
                ))
              }
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-brand-dark mb-2">Nutritional Information</h2>
              {meal.nutritional_info ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Calories</p>
                    <p className="text-xl font-bold">{meal.nutritional_info.calories}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Protein</p>
                    <p className="text-xl font-bold">{meal.nutritional_info.protein}g</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Carbs</p>
                    <p className="text-xl font-bold">{meal.nutritional_info.carbs}g</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Fat</p>
                    <p className="text-xl font-bold">{meal.nutritional_info.fat}g</p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 italic">Nutritional information not available</p>
              )}
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-2xl font-bold text-brand-dark mb-4">Leave Feedback</h2>
              {feedbackSuccess && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
                  Thank you for your feedback!
                </div>
              )}
              <form onSubmit={handleSubmitFeedback}>
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2">Rating</label>
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setRating(star)}
                        className="focus:outline-none"
                      >
                        <svg 
                          xmlns="http://www.w3.org/2000/svg" 
                          className="h-8 w-8" 
                          viewBox="0 0 20 20" 
                          fill={star <= rating ? "#FFD700" : "#E5E7EB"}
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      </button>
                    ))}
                  </div>
                </div>
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2">Comment (optional)</label>
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    className="input-field h-24"
                    placeholder="Share your thoughts about this meal..."
                  ></textarea>
                </div>
                <button
                  type="submit"
                  disabled={rating === 0 || submittingFeedback}
                  className={`btn-primary w-full ${(rating === 0 || submittingFeedback) ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Right column - Recipe and ingredients */}
        <div>
          <h1 className="text-3xl font-bold text-brand-dark mb-2">{meal.name}</h1>
          
          <div className="flex items-center text-gray-600 mb-6">
            {meal.cuisine_type && (
              <span className="flex items-center mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {meal.cuisine_type}
              </span>
            )}
            {meal.prep_time && (
              <span className="flex items-center mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {meal.prep_time + (meal.cook_time || 0)} min
              </span>
            )}
            {meal.servings && (
              <span className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                {meal.servings} servings
              </span>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 mb-6">
            <h2 className="text-2xl font-bold text-brand-dark mb-4">Ingredients</h2>
            <ul className="space-y-2">
              {meal.ingredients && meal.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-brand-primary mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {ingredient}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-2xl font-bold text-brand-dark mb-4">Preparation Steps</h2>
            <ol className="space-y-4">
              {meal.recipe_steps && meal.recipe_steps.map((step, index) => (
                <li key={index} className="flex">
                  <span className="flex-shrink-0 h-6 w-6 rounded-full bg-brand-primary text-white flex items-center justify-center mr-3">
                    {index + 1}
                  </span>
                  <p className="text-gray-700">{step}</p>
                </li>
              ))}
            </ol>
          </div>

          {meal.feedback && meal.feedback.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6 mt-6">
              <h2 className="text-2xl font-bold text-brand-dark mb-4">User Feedback</h2>
              <div className="space-y-4">
                {meal.feedback.slice(0, 3).map((fb, index) => (
                  <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
                    <div className="flex items-center mb-2">
                      <div className="flex text-yellow-400">
                        {[...Array(5)].map((_, i) => (
                          <svg 
                            key={i}
                            xmlns="http://www.w3.org/2000/svg" 
                            className="h-5 w-5" 
                            viewBox="0 0 20 20" 
                            fill={i < fb.rating ? "currentColor" : "#E5E7EB"}
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <span className="text-sm text-gray-500 ml-2">
                        {new Date(fb.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                    {fb.comment && <p className="text-gray-700">{fb.comment}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MealDetails;
