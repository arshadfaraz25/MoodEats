import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  ArcElement,
  Title, 
  Tooltip, 
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  ArcElement,
  Title, 
  Tooltip, 
  Legend,
  Filler
);

const AdminAnalytics = () => {
  const [analyticsType, setAnalyticsType] = useState('user');
  const [timeRange, setTimeRange] = useState('month');
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
        
        console.log(`${analyticsType} analytics response:`, response);
        
        // Handle both parsed JSON and string responses
        let analyticsData = response.data;
        
        // If the response is a string (raw JSON), parse it
        if (typeof response.data === 'string') {
          try {
            analyticsData = JSON.parse(response.data);
            console.log(`Parsed ${analyticsType} data from string:`, analyticsData);
          } catch (parseErr) {
            console.error(`Error parsing ${analyticsType} data:`, parseErr);
            throw new Error(`Failed to parse ${analyticsType} analytics data`);
          }
        }
        
        setData(analyticsData);
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
    
    // Generate mock data for user growth chart
    const userGrowthData = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'User Growth',
          data: [data.total_users * 0.5, data.total_users * 0.6, data.total_users * 0.7, 
                data.total_users * 0.8, data.total_users * 0.9, data.total_users],
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
          fill: true
        }
      ]
    };
    
    // Generate data for user activity chart using real data
    const userActivityData = {
      labels: ['Active Users', 'Inactive Users'],
      datasets: [
        {
          label: 'User Activity',
          data: [
            data.active_users || 0, 
            (data.total_users || 0) - (data.active_users || 0)
          ],
          backgroundColor: [
            'rgba(54, 162, 235, 0.6)',
            'rgba(200, 200, 200, 0.6)'
          ],
          borderWidth: 1
        }
      ]
    };
    
    return (
      <div className="space-y-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">User Growth</h3>
          <div className="h-64">
            <Line 
              data={userGrowthData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'User Growth Over Time'
                  }
                }
              }}
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">User Activity</h3>
            <div className="h-48">
              <Doughnut 
                data={userActivityData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'right',
                    },
                    title: {
                      display: true,
                      text: `Active vs Inactive Users (Total: ${data.total_users || 0})`,
                      font: {
                        size: 12
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">User Activity Metrics</h3>
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
        </div>
      </div>
    );
  };
  
  const renderMealAnalytics = () => {
    if (!data) return null;
    
    // Generate data for cuisine popularity chart from real data
    const cuisineData = {
      labels: data.category_distribution ? data.category_distribution.map(item => item.category) : ['Italian', 'Mexican', 'Asian', 'American', 'Other'],
      datasets: [
        {
          label: 'Cuisine Popularity',
          data: data.category_distribution ? data.category_distribution.map(item => item.count) : [25, 18, 22, 15, 20],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)'
          ],
          borderWidth: 1
        }
      ]
    };
    
    // Get total views and ratings for meal metrics
    const totalViews = data.top_rated_meals ? 
      data.top_rated_meals.reduce((sum, meal) => sum + (meal.view_count || 0), 0) : 0;
    
    const totalRatings = data.top_rated_meals ? 
      data.top_rated_meals.reduce((sum, meal) => sum + (meal.rating_count || 0), 0) : 0;
    
    // Calculate average rating across all meals
    const avgRating = data.top_rated_meals && data.top_rated_meals.length > 0 ? 
      data.top_rated_meals.reduce((sum, meal) => sum + (meal.average_rating || 0), 0) / data.top_rated_meals.length : 0;
    
    // Generate meal metrics data
    const mealMetricsData = {
      labels: ['Total Meals', 'Total Views', 'Total Ratings'],
      datasets: [
        {
          label: 'Meal Metrics',
          data: [
            data.total_meals || 0,
            totalViews,
            totalRatings
          ],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(75, 192, 192, 0.6)'
          ],
          borderWidth: 1
        }
      ]
    };
    
    // Generate data for meal type distribution (mock data)
    const mealTypeData = {
      labels: ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert'],
      datasets: [
        {
          label: 'Meal Type Distribution (Mock Data)',
          data: [20, 30, 35, 10, 5],
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
        }
      ]
    };
    
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
                    Rating
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.top_rated_meals && data.top_rated_meals.length > 0 ? (
                  data.top_rated_meals.map((meal, index) => (
                    <tr key={meal.id || index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {index + 1}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {meal.name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {meal.view_count || meal.rating_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {meal.average_rating ? meal.average_rating.toFixed(1) : '-'}/5
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="px-6 py-4 text-center text-sm text-gray-500">
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
            <div className="h-64">
              <Pie 
                data={cuisineData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'right',
                    }
                  }
                }}
              />
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Meal Metrics</h3>
            <div className="h-64">
              <Bar 
                data={mealMetricsData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false
                    },
                    title: {
                      display: true,
                      text: 'Meal Engagement Metrics',
                      font: {
                        size: 12
                      }
                    }
                  },
                  scales: {
                    y: {
                      beginAtZero: true
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Meal Type Distribution</h3>
            <div className="h-64">
              <Bar 
                data={mealTypeData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false
                    },
                    title: {
                      display: true,
                      text: 'Mock Data - Meal types not stored in database',
                      font: {
                        size: 12
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const renderMoodAnalytics = () => {
    if (!data) return null;
    
    // Generate data for mood distribution chart
    const moodDistributionData = {
      labels: data.mood_distribution ? data.mood_distribution.map(item => item.mood) : ['Happy', 'Sad', 'Stressed', 'Energetic', 'Tired'],
      datasets: [
        {
          label: 'Mood Distribution',
          data: data.mood_distribution ? data.mood_distribution.map(item => item.count) : [30, 15, 20, 25, 10],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)'
          ],
          borderWidth: 1
        }
      ]
    };
    
    // Process mood trends data for the chart
    let moodTrendsLabels = [];
    let moodTrendsDatasets = [];
    
    if (data.mood_trends && data.mood_trends.length > 0) {
      // Get unique dates and moods
      const uniqueDates = [...new Set(data.mood_trends.map(item => item.date))].sort();
      const uniqueMoods = [...new Set(data.mood_trends.map(item => item.mood))];
      
      moodTrendsLabels = uniqueDates;
      
      // Create a dataset for each mood
      uniqueMoods.forEach((mood, index) => {
        const moodData = uniqueDates.map(date => {
          const entry = data.mood_trends.find(item => item.date === date && item.mood === mood);
          return entry ? entry.count : 0;
        });
        
        moodTrendsDatasets.push({
          label: mood,
          data: moodData,
          borderColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 206, 86)',
            'rgb(75, 192, 192)',
            'rgb(153, 102, 255)'
          ][index % 5],
          backgroundColor: 'transparent',
          tension: 0.4
        });
      });
    } else {
      // Mock data if no real data available
      moodTrendsLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      moodTrendsDatasets = [
        {
          label: 'Happy',
          data: [10, 12, 8, 15, 20, 18, 15],
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'transparent',
          tension: 0.4
        },
        {
          label: 'Sad',
          data: [5, 8, 12, 7, 3, 5, 8],
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'transparent',
          tension: 0.4
        }
      ];
    }
    
    const moodTrendsData = {
      labels: moodTrendsLabels,
      datasets: moodTrendsDatasets
    };
    
    // Generate data for mood-meal correlation (mock data)
    const correlationData = {
      labels: data.meal_mood_correlations ? data.meal_mood_correlations.map(item => `${item.mood} - ${item.meal_type}`) : 
        ['Happy - Desserts', 'Sad - Comfort Food', 'Stressed - Healthy', 'Energetic - Protein-rich', 'Tired - Carbs'],
      datasets: [
        {
          label: 'Correlation Strength (Mock Data)',
          data: data.meal_mood_correlations ? data.meal_mood_correlations.map(item => item.correlation * 100) : [80, 70, 60, 90, 75],
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
        }
      ]
    };
    
    return (
      <div className="space-y-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Mood Distribution</h3>
          <div className="h-64">
            <Doughnut 
              data={moodDistributionData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'right',
                  }
                }
              }}
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Mood Trends</h3>
            <div className="h-64">
              <Line 
                data={moodTrendsData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'top',
                    }
                  },
                  scales: {
                    y: {
                      beginAtZero: true
                    }
                  }
                }}
              />
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Mood to Meal Correlation</h3>
            <div className="h-64">
              <Bar 
                data={correlationData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false
                    },
                    title: {
                      display: true,
                      text: 'Mock Data - Correlations not stored in database',
                      font: {
                        size: 12
                      }
                    }
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                      title: {
                        display: true,
                        text: 'Correlation Strength (%)'
                      }
                    }
                  }
                }}
              />
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
              <option value="year">Last 365 Days</option>
            </select>
          </div>
        </div>
      </div>
      
      {renderAnalyticsContent()}
    </div>
  );
};

export default AdminAnalytics;
