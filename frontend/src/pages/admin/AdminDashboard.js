import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI } from '../../services/api';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalMeals: 0,
    moodLogsToday: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        console.log('Fetching admin stats...');
        
        // Try a simpler approach - fetch each stat individually with error handling
        let userCount = 0;
        let mealCount = 0;
        let moodLogCount = 0;
        
        try {
          console.log('Fetching user analytics...');
          const userAnalytics = await adminAPI.getUserAnalytics();
          console.log('User analytics response:', userAnalytics);
          userCount = userAnalytics.data.total_users || 0;
        } catch (err) {
          console.error('Error fetching user analytics:', err);
        }
        
        try {
          console.log('Fetching meal analytics...');
          const mealAnalytics = await adminAPI.getMealAnalytics();
          console.log('Meal analytics response:', mealAnalytics);
          console.log('Meal analytics data type:', typeof mealAnalytics.data);
          console.log('Meal analytics data content:', JSON.stringify(mealAnalytics.data, null, 2));
          console.log('Total meals value:', mealAnalytics.data.total_meals);
          console.log('Total meals type:', typeof mealAnalytics.data.total_meals);
          
          // Ensure we're getting a number and not a string or other type
          // Handle both cases: if data is already parsed or if it's a string
          let mealData = mealAnalytics.data;
          
          // If the response is a string (raw JSON), parse it
          if (typeof mealAnalytics.data === 'string') {
            try {
              mealData = JSON.parse(mealAnalytics.data);
              console.log('Parsed meal data from string:', mealData);
            } catch (parseErr) {
              console.error('Error parsing meal data:', parseErr);
            }
          }
          
          // Extract and convert the total_meals value
          mealCount = parseInt(mealData.total_meals || 0);
          console.log('Final meal count used:', mealCount);
        } catch (err) {
          console.error('Error fetching meal analytics:', err);
        }
        
        try {
          console.log('Fetching mood analytics...');
          const moodAnalytics = await adminAPI.getMoodAnalytics();
          console.log('Mood analytics response:', moodAnalytics);
          
          // Use the today_logs_count directly from the backend response
          moodLogCount = moodAnalytics.data.today_logs_count || 0;
          console.log(`Today's mood logs count: ${moodLogCount}`);
        } catch (err) {
          console.error('Error fetching mood analytics:', err);
        }
        
        setStats({
          totalUsers: userCount,
          totalMeals: mealCount,
          moodLogsToday: moodLogCount
        });
        
        setError(null);
      } catch (err) {
        console.error('Error fetching admin stats:', err);
        setError(`Failed to load statistics: ${err.message || 'Unknown error'}`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-brand-dark mb-8">Admin Dashboard</h1>
      
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
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/admin/users" className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">User Management</h2>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-brand-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <p className="mt-2 text-gray-600">Manage users, view profiles, and handle user accounts.</p>
        </Link>
        
        <Link to="/admin/meals" className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Meal Management</h2>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-brand-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <p className="mt-2 text-gray-600">Add, edit, and remove meals from the database.</p>
        </Link>
        
        <Link to="/admin/analytics" className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Analytics</h2>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-brand-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="mt-2 text-gray-600">View user engagement, popular meals, and mood trends.</p>
        </Link>
      </div>
      
      <div className="mt-12 bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
        {loading ? (
          <div className="flex justify-center items-center h-24">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand-primary"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Total Users</p>
              <p className="text-2xl font-bold">{stats.totalUsers}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Total Meals</p>
              <p className="text-2xl font-bold">{stats.totalMeals}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Mood Logs Today</p>
              <p className="text-2xl font-bold">{stats.moodLogsToday}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
