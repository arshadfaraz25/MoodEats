/**
 * File name: App.js
 * Purpose: Main application component that handles routing and authentication.
 * Provides the structure for the MoodEats application.
 *
 * @author Arshad Faraz
 * @version 1.0.0
 */
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import MealDetails from './pages/MealDetails';
import MoodSelection from './pages/MoodSelection';
import Recommendations from './pages/Recommendations';
import Favorites from './pages/Favorites';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminMeals from './pages/admin/AdminMeals';
import AdminAnalytics from './pages/admin/AdminAnalytics';
import NotFound from './pages/NotFound';

// Auth Context
import { AuthProvider, useAuth } from './context/AuthContext';

// Protected Route Component
/**
 * Component that protects routes requiring authentication
 * Redirects to login page if user is not authenticated
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Admin Route Component
/**
 * Component that protects routes requiring admin privileges
 * Redirects to dashboard if user is not an admin
 */
const AdminRoute = ({ children }) => {
  const { isAuthenticated, user, loading } = useAuth();
  
  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  if (!isAuthenticated || !user.is_admin) {
    return <Navigate to="/dashboard" />;
  }
  
  return children;
};

/**
 * Main application content component with routing configuration
 */
function AppContent() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
          <Route path="/mood-selection" element={
            <ProtectedRoute>
              <MoodSelection />
            </ProtectedRoute>
          } />
          <Route path="/recommendations" element={
            <ProtectedRoute>
              <Recommendations />
            </ProtectedRoute>
          } />
          <Route path="/meal/:id" element={
            <ProtectedRoute>
              <MealDetails />
            </ProtectedRoute>
          } />
          <Route path="/favorites" element={
            <ProtectedRoute>
              <Favorites />
            </ProtectedRoute>
          } />
          
          {/* Admin Routes */}
          <Route path="/admin" element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          } />
          <Route path="/admin/users" element={
            <AdminRoute>
              <AdminUsers />
            </AdminRoute>
          } />
          <Route path="/admin/meals" element={
            <AdminRoute>
              <AdminMeals />
            </AdminRoute>
          } />
          <Route path="/admin/analytics" element={
            <AdminRoute>
              <AdminAnalytics />
            </AdminRoute>
          } />
          
          {/* 404 Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

/**
 * Root App component that wraps the application with the AuthProvider
 */
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
