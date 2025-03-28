import React, { useState, useEffect } from 'react';
import { moodAPI } from '../services/api';
import { Link } from 'react-router-dom';

const MoodHistory = ({ limit = 10 }) => {
  const [moodHistory, setMoodHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Emoji mapping for moods
  const moodEmojis = {
    'happy': '😊',
    'sad': '😔',
    'stressed': '😰',
    'relaxed': '😌',
    'energetic': '⚡',
    'tired': '😴',
    'hungry': '🍽️',
    'bored': '😒',
    'sick': '🤒',
    'celebratory': '🎉'
  };

  // Background color mapping for mood badges
  const moodColors = {
    'happy': 'bg-green-100 text-green-800',
    'sad': 'bg-blue-100 text-blue-800',
    'stressed': 'bg-yellow-100 text-yellow-800',
    'relaxed': 'bg-indigo-100 text-indigo-800',
    'energetic': 'bg-purple-100 text-purple-800',
    'tired': 'bg-gray-100 text-gray-800',
    'hungry': 'bg-orange-100 text-orange-800',
    'bored': 'bg-pink-100 text-pink-800',
    'sick': 'bg-red-100 text-red-800',
    'celebratory': 'bg-teal-100 text-teal-800'
  };

  // Function to deduplicate mood entries
  const deduplicateMoodEntries = (entries) => {
    // Group entries by exact timestamp to detect true duplicates
    const groupedByTimestamp = {};
    
    entries.forEach(entry => {
      const timestamp = entry.timestamp;
      
      if (!groupedByTimestamp[timestamp]) {
        groupedByTimestamp[timestamp] = [];
      }
      
      // Add to the group
      groupedByTimestamp[timestamp].push(entry);
    });
    
    // For each group, keep only one entry (the one with notes if available)
    const deduplicated = [];
    
    Object.values(groupedByTimestamp).forEach(group => {
      if (group.length === 1) {
        // Only one entry, no need to deduplicate
        deduplicated.push(group[0]);
      } else {
        // Multiple entries with same timestamp, prioritize the one with notes
        const entryWithNotes = group.find(entry => entry.notes);
        deduplicated.push(entryWithNotes || group[0]);
      }
    });
    
    // Sort by timestamp (newest first)
    return deduplicated.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  };

  useEffect(() => {
    const fetchMoodHistory = async () => {
      try {
        setLoading(true);
        const response = await moodAPI.getMoodHistory(limit);
        
        // Deduplicate entries before setting state
        const deduplicated = deduplicateMoodEntries(response.data);
        setMoodHistory(deduplicated);
        
        setError(null);
      } catch (err) {
        console.error('Error fetching mood history:', err);
        setError('Failed to load your mood history. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchMoodHistory();
  }, [limit]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
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

  if (moodHistory.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">You haven't logged any moods yet.</p>
        <Link to="/mood-selection" className="mt-4 inline-block btn-secondary">
          Log Your First Mood
        </Link>
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Mood
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Notes
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {moodHistory.map((entry) => (
            <tr key={entry._id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(entry.timestamp).toLocaleDateString()} {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${moodColors[entry.mood] || 'bg-gray-100 text-gray-800'}`}>
                  {entry.mood.charAt(0).toUpperCase() + entry.mood.slice(1)} {moodEmojis[entry.mood] || ''}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {entry.notes || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-brand-primary">
                <Link 
                  to={`/recommendations?mood=${entry.mood}`} 
                  className="hover:underline"
                >
                  View Recommendations
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MoodHistory;
