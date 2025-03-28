# MoodEats Application - System Design & Flow

## Overview
MoodEats is a web application designed to enhance meal planning by recommending meals based on users' emotional states. By connecting emotional well-being with mindful eating, MoodEats provides a personalized food selection experience. The application integrates sentiment analysis, user preferences, and external recipe databases to deliver tailored meal recommendations.

Don't use ML for recommendations.

## Tech stack

- Backend: Python Flask
- Frontend: html css javascript React Tailwind 
- Database: MongoDB

## Backend Architecture

The following classes facilitate application functionality:

### 1. `User` Class
- Manages user data such as authentication, preferences, and activity.

### 2. `MoodLog` Class
- Stores user mood selections and interactions for recommendation improvements.

### 3. `Meal` Class
- Defines meal properties, including name, ingredients, recipe, and nutritional info.

### 4. `Feedback` Class
- Handles user feedback and ratings for meal recommendations.

### 5. `NutritionalInfo` Class
- Stores details on meal calories, macronutrients, and dietary categorization.

### 6. `RecommendationEngine` Class
- Processes user mood, preferences, and history to generate personalized meal suggestions, Don't use ML for recommendations.

### 7. `UserPreferences` Class
- Tracks user settings such as dietary restrictions, preferred cuisines, and calorie goals.

### 8. `DatabaseManager` Class
- Centralized storage for users, meals, moods, and feedback data.


## Features

### User Features

#### Signup/Login
- Users can create accounts and log in securely.

#### Profile Setup (First-Time Login)
- Users provide:
  - Name & Contact Details
  - Dietary Restrictions
  - Cuisine Preferences
  - Calorie Goals
  - Address

#### Mood-Based Recommendations
- Users select their current mood (e.g., Happy, Stressed, Nostalgic, etc.).
- The system generates meal recommendations based on:
  - Mood
  - Preferences & Restrictions
  - Location-Based Availability
  - Past Selections & Feedback
- Results can be filtered by cuisine, dietary restrictions, and calorie range.

#### Meal Details
- Provides:
  - Recipe Instructions
  - Meal Images
  - Nutritional Information
- Users can:
  - Add meals to favorites
  - Provide feedback on recommendations
  - Track emotional eating patterns over time

#### Favorites Management
- Users can store and manage their favorite meals.

### Admin Features

#### User Management
- View and manage registered users.

#### Meal Management
- Add new meals to the database (single/multiple via CSV or JSON upload).
- Modify or remove meals.

#### Analytics & Reports
- Track user engagement, popular meals, and mood-based trends.
- Generate reports on app usage and meal preferences.

## Application Flow

### 1. Authentication
- Users access the homepage with login/signup options.
- First-time users complete their profile setup upon successful login.

### 2. Dashboard & Mood Selection
- Returning users land on a personalized dashboard.
- Users click "Get Recommendations" and select their current mood.

### 3. Meal Recommendations
- The system fetches meal options based on:
  - User Mood
  - Dietary Preferences & Restrictions
  - Location-Based Availability
  - Past Meal Choices & Feedback
- Results can be filtered and sorted. Don't use ML for recommendations.

### 4. Meal Details & Interaction
- Users can:
  - View recipe details
  - Mark meals as favorites
  - Provide feedback (ratings & comments)

### 5. Admin Panel
- Admin users can:
  - Manage users
  - Upload meals (CSV/JSON support)
  - View analytics reports


---

MoodEats is structured to provide a seamless and personalized experience for users while enabling efficient management through an admin panel. With its robust backend and intuitive interface, it aligns with the growing trend of health-conscious, experience-driven dining solutions.
