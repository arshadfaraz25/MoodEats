import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { userAPI } from '../services/api';
import MoodHistory from '../components/MoodHistory';

const Profile = () => {
  const { user, updateProfile, updatePreferences } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [showAllHistory, setShowAllHistory] = useState(false);
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  // Preferences form state
  const [preferencesForm, setPreferencesForm] = useState({
    dietary_restrictions: [],
    cuisines: [],
    calorie_goal: '',
    address: '',
    allergies: []
  });
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  // Available options for form selections
  const cuisineOptions = [
    'Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 
    'Thai', 'French', 'Mediterranean', 'American', 'Middle Eastern'
  ];
  
  const dietaryOptions = [
    'Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 
    'Keto', 'Paleo', 'Low-Carb', 'Low-Fat', 'Pescatarian'
  ];
  
  // Load user data on component mount
  useEffect(() => {
    const loadUserData = async () => {
      try {
        // Load profile data
        if (user) {
          setProfileForm({
            name: user.name || '',
            email: user.email || '',
            password: '',
            confirmPassword: ''
          });
        }
        
        // Load preferences data
        const prefsResponse = await userAPI.getPreferences();
        const prefs = prefsResponse.data;
        
        setPreferencesForm({
          dietary_restrictions: prefs.dietary_restrictions || [],
          cuisines: prefs.cuisines || [],
          calorie_goal: prefs.calorie_goal || '',
          address: prefs.address || '',
          allergies: prefs.allergies || []
        });
      } catch (error) {
        console.error('Error loading user data:', error);
        setError('Failed to load your profile data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    loadUserData();
  }, [user]);
  
  // Handle profile form changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Handle preferences form changes
  const handlePreferencesChange = (e) => {
    const { name, value } = e.target;
    setPreferencesForm(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Handle checkbox/multi-select changes
  const handleCheckboxChange = (field, value) => {
    setPreferencesForm(prev => {
      const currentValues = prev[field];
      if (currentValues.includes(value)) {
        return {
          ...prev,
          [field]: currentValues.filter(item => item !== value)
        };
      } else {
        return {
          ...prev,
          [field]: [...currentValues, value]
        };
      }
    });
  };
  
  // Handle allergies input (comma-separated)
  const handleAllergiesChange = (e) => {
    const allergiesText = e.target.value;
    setPreferencesForm(prev => ({
      ...prev,
      allergies: allergiesText.split(',').map(item => item.trim()).filter(Boolean)
    }));
  };
  
  // Save profile changes
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (profileForm.password && profileForm.password !== profileForm.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setError('');
    setSuccess('');
    setSaving(true);
    
    try {
      // Only send password if it was changed
      const updateData = {
        name: profileForm.name,
        email: profileForm.email
      };
      
      if (profileForm.password) {
        updateData.password = profileForm.password;
      }
      
      await updateProfile(updateData);
      setSuccess('Profile updated successfully');
      
      // Clear password fields
      setProfileForm(prev => ({
        ...prev,
        password: '',
        confirmPassword: ''
      }));
    } catch (err) {
      setError('Failed to update profile. Please try again.');
      console.error('Profile update error:', err);
    } finally {
      setSaving(false);
    }
  };
  
  // Save preferences changes
  const handlePreferencesSubmit = async (e) => {
    e.preventDefault();
    
    setError('');
    setSuccess('');
    setSaving(true);
    
    try {
      await updatePreferences(preferencesForm);
      setSuccess('Preferences updated successfully');
    } catch (err) {
      setError('Failed to update preferences. Please try again.');
      console.error('Preferences update error:', err);
    } finally {
      setSaving(false);
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
      <h1 className="text-3xl font-bold text-brand-dark mb-8">Your Profile</h1>
      
      {/* Tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('profile')}
            className={`${
              activeTab === 'profile'
                ? 'border-brand-primary text-brand-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Account Information
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            className={`${
              activeTab === 'preferences'
                ? 'border-brand-primary text-brand-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Dietary Preferences
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`${
              activeTab === 'history'
                ? 'border-brand-primary text-brand-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Mood History
          </button>
        </nav>
      </div>
      
      {/* Success/Error Messages */}
      {success && (
        <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-700">{success}</p>
            </div>
          </div>
        </div>
      )}
      
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
      
      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">Account Information</h2>
          <form onSubmit={handleProfileSubmit}>
            <div className="space-y-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <div className="mt-1">
                  <input
                    id="name"
                    name="name"
                    type="text"
                    value={profileForm.name}
                    onChange={handleProfileChange}
                    className="input-field"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <div className="mt-1">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={profileForm.email}
                    onChange={handleProfileChange}
                    className="input-field"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  New Password (leave blank to keep current)
                </label>
                <div className="mt-1">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    value={profileForm.password}
                    onChange={handleProfileChange}
                    className="input-field"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                  Confirm New Password
                </label>
                <div className="mt-1">
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    value={profileForm.confirmPassword}
                    onChange={handleProfileChange}
                    className="input-field"
                  />
                </div>
              </div>
              
              <div>
                <button
                  type="submit"
                  disabled={saving}
                  className={`btn-primary ${saving ? 'opacity-70 cursor-not-allowed' : ''}`}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
      
      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">Dietary Preferences</h2>
          <form onSubmit={handlePreferencesSubmit}>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dietary Restrictions
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {dietaryOptions.map(option => (
                    <div key={option} className="flex items-center">
                      <input
                        id={`dietary-${option}`}
                        type="checkbox"
                        checked={preferencesForm.dietary_restrictions.includes(option)}
                        onChange={() => handleCheckboxChange('dietary_restrictions', option)}
                        className="h-4 w-4 text-brand-primary focus:ring-brand-primary border-gray-300 rounded"
                      />
                      <label htmlFor={`dietary-${option}`} className="ml-2 block text-sm text-gray-900">
                        {option}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Cuisines
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {cuisineOptions.map(cuisine => (
                    <div key={cuisine} className="flex items-center">
                      <input
                        id={`cuisine-${cuisine}`}
                        type="checkbox"
                        checked={preferencesForm.cuisines.includes(cuisine)}
                        onChange={() => handleCheckboxChange('cuisines', cuisine)}
                        className="h-4 w-4 text-brand-primary focus:ring-brand-primary border-gray-300 rounded"
                      />
                      <label htmlFor={`cuisine-${cuisine}`} className="ml-2 block text-sm text-gray-900">
                        {cuisine}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <label htmlFor="calorie_goal" className="block text-sm font-medium text-gray-700">
                  Daily Calorie Goal
                </label>
                <div className="mt-1">
                  <input
                    id="calorie_goal"
                    name="calorie_goal"
                    type="number"
                    min="0"
                    value={preferencesForm.calorie_goal}
                    onChange={handlePreferencesChange}
                    className="input-field"
                    placeholder="e.g., 2000"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="address" className="block text-sm font-medium text-gray-700">
                  Delivery Address (optional)
                </label>
                <div className="mt-1">
                  <input
                    id="address"
                    name="address"
                    type="text"
                    value={preferencesForm.address}
                    onChange={handlePreferencesChange}
                    className="input-field"
                    placeholder="Enter your delivery address"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="allergies" className="block text-sm font-medium text-gray-700">
                  Allergies (comma-separated)
                </label>
                <div className="mt-1">
                  <input
                    id="allergies"
                    name="allergies"
                    type="text"
                    value={preferencesForm.allergies.join(', ')}
                    onChange={handleAllergiesChange}
                    className="input-field"
                    placeholder="e.g., peanuts, shellfish, dairy"
                  />
                </div>
              </div>
              
              <div>
                <button
                  type="submit"
                  disabled={saving}
                  className={`btn-primary ${saving ? 'opacity-70 cursor-not-allowed' : ''}`}
                >
                  {saving ? 'Saving...' : 'Save Preferences'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
      
      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">Your Mood History</h2>
          <p className="text-gray-600 mb-6">
            Track your mood patterns over time and see how they relate to your meal choices.
          </p>
          
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <MoodHistory limit={showAllHistory ? 0 : 10} />
          </div>
          
          <div className="mt-6 text-center">
            <button 
              className="btn-secondary" 
              onClick={() => setShowAllHistory(!showAllHistory)}
            >
              {showAllHistory ? 'Show Less' : 'View Full History'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
