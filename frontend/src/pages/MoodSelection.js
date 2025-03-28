import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { moodAPI } from '../services/api';

const MoodSelection = () => {
  const [moods, setMoods] = useState([]);
  const [selectedMood, setSelectedMood] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMoods = async () => {
      try {
        const response = await moodAPI.getAvailableMoods();
        setMoods(response.data);
      } catch (error) {
        console.error('Error fetching moods:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMoods();
  }, []);

  const handleMoodSelect = (mood) => {
    setSelectedMood(mood);
  };

  const handleSubmit = async () => {
    if (!selectedMood || submitting) return;

    try {
      setSubmitting(true);
      // Log the mood
      await moodAPI.logMood({ mood: selectedMood.id, notes: `Selected from mood selection page` });
      
      // Navigate to recommendations with the selected mood
      navigate(`/recommendations?mood=${selectedMood.id}`);
    } catch (error) {
      console.error('Error logging mood:', error);
      setSubmitting(false);
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
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-brand-dark mb-4">How are you feeling today?</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Select your current mood and we'll recommend meals that complement your emotional state.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
        {moods.map((mood) => (
          <div
            key={mood.id}
            className={`mood-card ${selectedMood?.id === mood.id ? 'active' : ''}`}
            onClick={() => handleMoodSelect(mood)}
          >
            <div className="text-4xl mb-2">{mood.emoji}</div>
            <h3 className="text-lg font-medium">{mood.name}</h3>
            <p className="text-sm text-gray-500 text-center mt-1">{mood.description}</p>
          </div>
        ))}
      </div>

      <div className="mt-12 text-center">
        <button
          className={`btn-primary ${!selectedMood || submitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={!selectedMood || submitting}
          onClick={handleSubmit}
        >
          {submitting ? 'Submitting...' : 'Get Recommendations'}
        </button>
      </div>

      {/* Mood explanation section */}
      <div className="mt-16 bg-white rounded-xl shadow-md p-6 max-w-4xl mx-auto">
        <h2 className="text-xl font-semibold mb-4">Why Mood Matters for Eating</h2>
        <p className="text-gray-600 mb-4">
          Your emotional state can significantly influence your food preferences and nutritional needs. 
          MoodEats uses this connection to suggest meals that may help enhance your current mood or provide comfort.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div className="bg-brand-bg p-4 rounded-lg">
            <h3 className="font-medium mb-2">When You're Happy</h3>
            <p className="text-sm text-gray-600">
              Celebratory foods can enhance your positive mood, while colorful, nutrient-rich options can help maintain your energy.
            </p>
          </div>
          
          <div className="bg-brand-bg p-4 rounded-lg">
            <h3 className="font-medium mb-2">When You're Stressed</h3>
            <p className="text-sm text-gray-600">
              Foods rich in magnesium and vitamin C can help reduce stress levels, while comfort foods may provide emotional relief.
            </p>
          </div>
          
          <div className="bg-brand-bg p-4 rounded-lg">
            <h3 className="font-medium mb-2">When You're Tired</h3>
            <p className="text-sm text-gray-600">
              Iron-rich and protein-packed meals can help combat fatigue, while complex carbohydrates provide sustained energy.
            </p>
          </div>
          
          <div className="bg-brand-bg p-4 rounded-lg">
            <h3 className="font-medium mb-2">When You're Nostalgic</h3>
            <p className="text-sm text-gray-600">
              Traditional recipes and childhood favorites can provide comfort and emotional connection through food memories.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoodSelection;
