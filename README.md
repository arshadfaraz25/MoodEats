# MoodEats

MoodEats is a web application designed to enhance meal planning by recommending meals based on users' emotional states. By connecting emotional well-being with mindful eating, MoodEats provides a personalized food selection experience.

## Features

- **Mood-Based Recommendations**: Get meal suggestions tailored to your current emotional state
- **User Profiles**: Save your dietary preferences, restrictions, and favorite meals
- **Recipe Details**: Access comprehensive information about each meal, including nutritional data
- **Admin Panel**: Manage users, meals, and view analytics (admin access only)

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: React, HTML, CSS, JavaScript, Tailwind CSS
- **Database**: MongoDB

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB

### Installation

1. Clone the repository
```
git clone 
cd moodeats
```

2. Set up the backend
```
pip install -r requirements.txt
cd backend
python app.py
```

3. Set up the frontend
```
cd frontend
npm install
npm start
```

4. Access the application at `http://localhost:3000`

## Project Structure

```
moodeats/
├── backend/              # Flask server
│   ├── models/           # Database models
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   ├── utils/            # Helper functions
│   └── app.py            # Main application file
├── frontend/             # React application
│   ├── public/           # Static files
│   ├── src/              # Source code
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Application pages
│   │   ├── services/     # API services
│   │   └── App.js        # Main component
├── docs/                 # Documentation
└── README.md             # Project overview
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
