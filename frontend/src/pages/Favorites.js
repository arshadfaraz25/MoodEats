import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import MealCard from '../components/MealCard';
import axios from 'axios';

const Favorites = () => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [debugInfo, setDebugInfo] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    const checkSession = async () => {
      try {
        console.log('Checking session...');
        const response = await axios.get('/api/users/check-session', { withCredentials: true });
        console.log('Session check response:', response.data);
        setIsAuthenticated(response.data.authenticated);
        setDebugInfo(prev => ({ ...prev, sessionCheck: response.data }));
        
        if (!response.data.authenticated) {
          console.log('User not authenticated, redirecting to login');
          setError('Please log in to view your favorites');
          setTimeout(() => {
            navigate('/login');
          }, 2000);
          return false;
        }
        return true;
      } catch (error) {
        console.error('Error checking session:', error);
        setDebugInfo(prev => ({ 
          ...prev, 
          sessionCheckError: { 
            message: error.message,
            status: error.response?.status,
            data: error.response?.data
          } 
        }));
        setIsAuthenticated(false);
        setError('Authentication error. Please log in again.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
        return false;
      }
    };

    const fetchFavorites = async () => {
      try {
        // First check if user is authenticated
        const isAuth = await checkSession();
        if (!isAuth) return;
        
        console.log('Fetching favorites...');
        const response = await userAPI.getFavorites();
        console.log('Favorites response:', response);
        console.log('Favorites data:', response.data);
        
        setDebugInfo(prev => ({ 
          ...prev, 
          favoritesResponse: {
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            data: response.data
          }
        }));
        
        if (Array.isArray(response.data)) {
          setFavorites(response.data);
        } else {
          console.error('Unexpected response format:', response.data);
          setFavorites([]);
          setError('Received invalid data format from server');
        }
      } catch (error) {
        console.error('Error fetching favorites:', error);
        setDebugInfo(prev => ({ 
          ...prev, 
          favoritesError: { 
            message: error.message,
            status: error.response?.status,
            data: error.response?.data,
            stack: error.stack
          } 
        }));
        
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

    fetchFavorites();
  }, [navigate]);

  const handleFavoriteToggle = async (mealId, isFavorite) => {
    console.log('Toggle favorite:', mealId, isFavorite);
    if (!isFavorite) {
      try {
        // Remove from favorites in the backend
        await userAPI.removeFavorite(mealId);
        // Remove from local state
        setFavorites(prev => prev.filter(meal => meal._id !== mealId));
      } catch (error) {
        console.error('Error removing favorite:', error);
        // If there's an error, refresh the favorites list
        try {
          const response = await userAPI.getFavorites();
          setFavorites(response.data);
        } catch (refreshError) {
          console.error('Error refreshing favorites:', refreshError);
        }
      }
    }
  };

  const handleRetry = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Retrying to fetch favorites...');
      const response = await userAPI.getFavorites();
      console.log('Retry response:', response);
      
      if (Array.isArray(response.data)) {
        setFavorites(response.data);
      } else {
        console.error('Unexpected retry response format:', response.data);
        setFavorites([]);
        setError('Received invalid data format from server');
      }
    } catch (error) {
      console.error('Error during retry:', error);
      setError('Failed to load your favorites. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated && error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center py-16 bg-white rounded-xl shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">Authentication Required</h3>
          <p className="mt-2 text-red-500 max-w-md mx-auto">
            {error}
          </p>
          <div className="mt-6">
            <Link to="/login" className="btn-primary">
              Log In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-brand-dark">Your Favorite Meals</h1>
        <Link to="/mood-selection" className="btn-primary">
          Discover More Meals
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
        </div>
      ) : error && isAuthenticated ? (
        <div className="text-center py-16 bg-white rounded-xl shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">Error Loading Favorites</h3>
          <p className="mt-2 text-red-500 max-w-md mx-auto">
            {error}
          </p>
          <div className="mt-6">
            <button onClick={handleRetry} className="btn-primary">
              Try Again
            </button>
          </div>
          
          {/* Debug information - only show in development */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-8 text-left bg-gray-100 p-4 rounded-lg overflow-auto max-h-96">
              <h4 className="font-bold mb-2">Debug Information:</h4>
              <pre className="text-xs">{JSON.stringify(debugInfo, null, 2)}</pre>
            </div>
          )}
        </div>
      ) : favorites.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map(meal => (
            <MealCard 
              key={meal._id} 
              meal={meal} 
              isFavorite={true}
              onFavoriteToggle={handleFavoriteToggle}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-xl shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No favorites yet</h3>
          <p className="mt-2 text-gray-500 max-w-md mx-auto">
            You haven't added any meals to your favorites yet. Explore recommendations based on your mood and save the ones you love!
          </p>
          <div className="mt-6">
            <Link to="/mood-selection" className="btn-primary">
              Get Meal Recommendations
            </Link>
          </div>
        </div>
      )}

      {favorites.length > 0 && (
        <div className="mt-12 bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Organize Your Favorites</h2>
          <p className="text-gray-600 mb-4">
            Your favorite meals are always available here for quick access. Remove items by clicking the heart icon.
          </p>
          <div className="flex flex-wrap gap-2">
            <button className="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 hover:bg-gray-200">
              Sort by Name
            </button>
            <button className="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 hover:bg-gray-200">
              Sort by Date Added
            </button>
            <button className="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 hover:bg-gray-200">
              Filter by Cuisine
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Favorites;
