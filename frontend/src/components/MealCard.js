/**
 * File name: MealCard.js
 * Purpose: Reusable meal card component for displaying meal information.
 * Handles meal display, favorite toggling, and navigation to meal details.
 *
 * @author Arshad Faraz
 * @version 1.0.0
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { userAPI } from '../services/api';

const MealCard = ({ meal, isFavorite, onFavoriteToggle }) => {
  const { isAuthenticated } = useAuth();
  
  const handleFavoriteToggle = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Toggling favorite for meal:', meal._id, 'Current favorite status:', isFavorite);
    
    if (!isAuthenticated) {
      console.log('User not authenticated, cannot toggle favorite');
      return;
    }
    
    try {
      if (isFavorite) {
        console.log('Removing meal from favorites:', meal._id);
        await userAPI.removeFavorite(meal._id);
      } else {
        console.log('Adding meal to favorites:', meal._id);
        const response = await userAPI.addFavorite(meal._id);
        console.log('Add favorite response:', response);
      }
      
      if (onFavoriteToggle) {
        console.log('Calling onFavoriteToggle with:', meal._id, !isFavorite);
        onFavoriteToggle(meal._id, !isFavorite);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };
  
  return (
    <div className="meal-card group relative">
      <Link to={`/meal/${meal._id}`} className="block">
        <div className="relative">
          <img 
            src={meal.image_url || 'https://via.placeholder.com/300x200?text=No+Image'} 
            alt={meal.name}
            className="w-full h-48 object-cover rounded-t-xl"
          />
          <button
            onClick={handleFavoriteToggle}
            className="absolute top-3 right-3 p-2 rounded-full bg-white shadow-md hover:scale-110 transition-transform"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-5 w-5 ${isFavorite ? "text-brand-primary" : "text-gray-400"}`}
              fill={isFavorite ? "currentColor" : "none"} 
              viewBox="0 0 24 24" 
              stroke="currentColor"
              strokeWidth={isFavorite ? "0" : "2"}
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" 
              />
            </svg>
          </button>
        </div>
        
        <div className="p-4">
          <div className="flex justify-between items-start">
            <h3 className="text-lg font-medium text-brand-dark truncate">{meal.name}</h3>
            {meal.nutritional_info && (
              <span className="text-sm font-medium text-gray-500">
                {meal.nutritional_info.calories} cal
              </span>
            )}
          </div>
          
          <div className="mt-1 flex items-center">
            {meal.cuisine_type && (
              <span className="text-sm text-gray-500">{meal.cuisine_type}</span>
            )}
            {meal.prep_time && (
              <span className="text-sm text-gray-500 ml-auto">
                {meal.prep_time + (meal.cook_time || 0)} min
              </span>
            )}
          </div>
          
          <div className="mt-3 flex flex-wrap gap-1">
            {meal.mood_tags && meal.mood_tags.slice(0, 3).map((tag, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-primary bg-opacity-10 text-brand-primary"
              >
                {tag}
              </span>
            ))}
            {meal.nutritional_info && meal.nutritional_info.dietary_tags && 
              meal.nutritional_info.dietary_tags.slice(0, 2).map((tag, index) => (
                <span 
                  key={`diet-${index}`}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-secondary bg-opacity-10 text-brand-secondary"
                >
                  {tag}
                </span>
              ))
            }
          </div>
        </div>
      </Link>
    </div>
  );
};

export default MealCard;
