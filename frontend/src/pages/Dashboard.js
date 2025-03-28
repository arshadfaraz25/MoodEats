import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { mealAPI, moodAPI, userAPI } from '../services/api';
import MealCard from '../components/MealCard';

const Dashboard = () => {
  const { user } = useAuth();
  const [recentMoods, setRecentMoods] = useState([]);
  const [favoritesMeals, setFavoritesMeals] = useState([]);
  const [personalizedMeals, setPersonalizedMeals] = useState([]);
  const [loading, setLoading] = useState({
    moods: true,
    favorites: true,
    personalized: true
  });
  const [availableMoods, setAvailableMoods] = useState([]);

  useEffect(() => {
    const fetchMoods = async () => {
      try {
        const response = await moodAPI.getAvailableMoods();
        setAvailableMoods(response.data);
      } catch (error) {
        console.error('Error fetching available moods:', error);
      }
    };

    fetchMoods();
  }, []);

  useEffect(() => {
    const fetchRecentMoods = async () => {
      try {
        const response = await moodAPI.getMoodHistory(5);
        
        // Filter out duplicate moods with the same mood type and date
        const uniqueMoods = [];
        const moodDateMap = new Map();
        
        response.data.forEach(mood => {
          const moodDate = new Date(mood.timestamp).toLocaleDateString();
          const key = `${mood.mood}-${moodDate}`;
          
          if (!moodDateMap.has(key)) {
            moodDateMap.set(key, true);
            uniqueMoods.push(mood);
          } else {
            console.log(`Filtered out duplicate mood: ${mood.mood} on ${moodDate}`);
          }
        });
        
        console.log(`Original moods: ${response.data.length}, Unique moods: ${uniqueMoods.length}`);
        setRecentMoods(uniqueMoods);
      } catch (error) {
        console.error('Error fetching recent moods:', error);
      } finally {
        setLoading(prev => ({ ...prev, moods: false }));
      }
    };

    const fetchFavorites = async () => {
      try {
        const response = await userAPI.getFavorites();
        setFavoritesMeals(response.data);
      } catch (error) {
        console.error('Error fetching favorites:', error);
      } finally {
        setLoading(prev => ({ ...prev, favorites: false }));
      }
    };

    const fetchPersonalizedMeals = async () => {
      try {
        const response = await mealAPI.getRandomMeals(6);
        setPersonalizedMeals(response.data);
      } catch (error) {
        console.error('Error fetching personalized meals:', error);
      } finally {
        setLoading(prev => ({ ...prev, personalized: false }));
      }
    };

    fetchRecentMoods();
    fetchFavorites();
    fetchPersonalizedMeals();
  }, []);

  // Helper function to get mood emoji and name
  const getMoodInfo = (moodId) => {
    const mood = availableMoods.find(m => m.id === moodId);
    return mood ? { emoji: mood.emoji, name: mood.name } : { emoji: '😊', name: moodId };
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-brand-primary to-brand-secondary rounded-xl text-white p-8 mb-10">
        <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.name || 'Friend'}!</h1>
        <p className="text-xl opacity-90">
          How are you feeling today? Let's find the perfect meal for your mood.
        </p>
        <div className="mt-6">
          <Link to="/mood-selection" className="btn-secondary">
            Get Recommendations
          </Link>
        </div>
      </div>

      {/* Mood History Section */}
      <div className="mb-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-brand-dark">Your Recent Moods</h2>
          <Link to="/mood-selection" className="text-brand-primary hover:underline">
            Log new mood
          </Link>
        </div>

        {loading.moods ? (
          <div className="flex justify-center items-center h-24">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand-primary"></div>
          </div>
        ) : recentMoods.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            {recentMoods.map((mood, index) => {
              const moodInfo = getMoodInfo(mood.mood);
              return (
                <div key={index} className="bg-white rounded-xl shadow-sm p-4 text-center">
                  <div className="text-3xl mb-2">{moodInfo.emoji}</div>
                  <h3 className="font-medium">{moodInfo.name}</h3>
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
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-6 text-center">
            <p className="text-gray-600">You haven't logged any moods yet.</p>
            <Link
              to="/mood-selection"
              className="text-brand-primary hover:underline mt-2 inline-block"
            >
              Log your first mood
            </Link>
          </div>
        )}
      </div>

      {/* Favorites Section */}
      <div className="mb-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-brand-dark">Your Favorites</h2>
          <Link to="/favorites" className="text-brand-primary hover:underline">
            See all
          </Link>
        </div>

        {loading.favorites ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand-primary"></div>
          </div>
        ) : favoritesMeals.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {favoritesMeals.slice(0, 3).map(meal => (
              <MealCard 
                key={meal._id} 
                meal={meal} 
                isFavorite={true}
                onFavoriteToggle={(mealId) => {
                  setFavoritesMeals(prev => prev.filter(m => m._id !== mealId));
                }}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-6 text-center">
            <p className="text-gray-600">You haven't added any favorites yet.</p>
            <Link
              to="/mood-selection"
              className="text-brand-primary hover:underline mt-2 inline-block"
            >
              Discover meals
            </Link>
          </div>
        )}
      </div>

      {/* Personalized Recommendations Section */}
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-brand-dark">Recommended For You</h2>
          <Link to="/mood-selection" className="text-brand-primary hover:underline">
            More recommendations
          </Link>
        </div>

        {loading.personalized ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand-primary"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {personalizedMeals.slice(0, 3).map(meal => (
              <MealCard 
                key={meal._id} 
                meal={meal} 
                isFavorite={favoritesMeals.some(fav => fav._id === meal._id)}
                onFavoriteToggle={(mealId, isFav) => {
                  if (isFav) {
                    // Add to favorites (would be handled by the MealCard component)
                  } else {
                    // Remove from favorites if it was there
                    setFavoritesMeals(prev => prev.filter(m => m._id !== mealId));
                  }
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
