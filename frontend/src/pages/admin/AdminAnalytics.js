import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';

const AdminAnalytics = () => {
  const [analyticsType, setAnalyticsType] = useState('user');
  const [timeRange, setTimeRange] = useState('week');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        let response;
        
        switch (analyticsType) {
          case 'user':
            response = await adminAPI.getUserAnalytics(timeRange);
            break;
          case 'meal':
            response = await adminAPI.getMealAnalytics(timeRange);
            break;
          case 'mood':
            response = await adminAPI.getMoodAnalytics(timeRange);
            break;
          default:
            response = await adminAPI.getUserAnalytics(timeRange);
        }
        
        setData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching analytics:', err);
        setError('Failed to load analytics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalytics();
  }, [analyticsType, timeRange]);
  
  const renderUserAnalytics = () => {
    if (!data) return null;
    
    return (
      <div className="space-y-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">User Growth</h3>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">User growth chart would display here</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">User Activity</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">Active Users</span>
                <span className="font-medium">{data.active_users || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">New Registrations</span>
                <span className="font-medium">{data.new_registrations || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">Average Session Duration</span>
                <span className="font-medium">{data.avg_session_duration || '0 mins'}</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">User Demographics</h3>
            <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Demographics chart would display here</p>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const renderMealAnalytics = () => {
    if (!data) return null;
    
    return (
      <div className="space-y-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Most Popular Meals</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meal
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Views
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recommendations
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Feedback Score
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.popular_meals && data.popular_meals.length > 0 ? (
                  data.popular_meals.map((meal, index) => (
                    <tr key={meal._id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {index + 1}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
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
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {meal.views || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {meal.recommendations || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {meal.feedback_score ? meal.feedback_score.toFixed(1) : '-'}/5
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">
                      No meal data available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Cuisine Popularity</h3>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Cuisine chart would display here</p>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Meal Type Distribution</h3>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Meal type chart would display here</p>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const renderMoodAnalytics = () => {
    if (!data) return null;
    
    return (
      <div className="space-y-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Mood Distribution</h3>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Mood distribution chart would display here</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Mood Trends</h3>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Mood trends chart would display here</p>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Mood to Meal Correlation</h3>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Correlation chart would display here</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Most Common Moods</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {data.common_moods && data.common_moods.length > 0 ? (
              data.common_moods.map((mood, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-brand-primary mb-1">{mood.count}</div>
                  <div className="text-sm text-gray-500">{mood.mood}</div>
                </div>
              ))
            ) : (
              <div className="col-span-5 text-center text-sm text-gray-500 py-4">
                No mood data available
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
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
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-brand-dark mb-8">Analytics Dashboard</h1>
      
      <div className="mb-8 bg-white rounded-xl shadow-md p-4">
        <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <div>
            <label htmlFor="analytics-type" className="block text-sm font-medium text-gray-700 mb-1">
              Analytics Type
            </label>
            <select
              id="analytics-type"
              value={analyticsType}
              onChange={(e) => setAnalyticsType(e.target.value)}
              className="input-field"
            >
              <option value="user">User Analytics</option>
              <option value="meal">Meal Analytics</option>
              <option value="mood">Mood Analytics</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="time-range" className="block text-sm font-medium text-gray-700 mb-1">
              Time Range
            </label>
            <select
              id="time-range"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="input-field"
            >
              <option value="day">Last 24 Hours</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
              <option value="year">Last Year</option>
            </select>
          </div>
        </div>
      </div>
      
      {renderAnalyticsContent()}
    </div>
  );
};

export default AdminAnalytics;
