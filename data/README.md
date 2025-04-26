# MoodEats Sample Data

This directory contains sample data and scripts to populate the MongoDB database for the MoodEats application.

**Author:** Arshad Faraz  
**Version:** 1.0.0

## Files

- `sample_meals.json` - Contains sample meal data with recipes, nutritional information, and mood tags
- `sample_moods.json` - Contains mood definitions with descriptions and food recommendations
- `load_sample_data.py` - Script to load meals, users, mood logs, and favorites into the database
- `load_moods.py` - Script to load mood definitions into the database
- `generate_feedback.py` - Script to generate sample user feedback for meals

## Usage

### Prerequisites

Make sure you have MongoDB running locally on the default port (27017).

### Loading Sample Data

1. **Load all sample data (meals, users, mood logs, favorites)**:

```bash
python load_sample_data.py
```

This script will:
- Clear existing collections
- Load sample meals from `sample_meals.json`
- Create sample users (admin and regular users)
- Generate sample mood logs for each user
- Add favorite meals for each user

2. **Load mood definitions only**:

```bash
python load_moods.py
```

3. **Generate sample feedback for meals**:

```bash
python generate_feedback.py
```

## Sample User Credentials

After running `load_sample_data.py`, the following user accounts will be available:

- **Admin User**:
  - Email: admin@moodeats.com
  - Password: adminpassword

- **Regular Users**:
  - Email: john@example.com
  - Password: password123
  
  - Email: jane@example.com
  - Password: password123
  
  - Email: bob@example.com
  - Password: password123

## Data Structure

### Meals

Each meal in `sample_meals.json` includes:
- Name and description
- List of ingredients
- Step-by-step recipe instructions
- Image URL
- Preparation and cooking time
- Cuisine and meal type
- Mood tags (which moods the meal is suitable for)
- Nutritional information and dietary tags

### Moods

Each mood in `sample_moods.json` includes:
- ID and name
- Description
- Emoji representation
- Color code
- Recommended foods for this mood
- Foods to avoid for this mood

## Customization

You can modify the sample data files to add your own meals and moods before running the scripts.
