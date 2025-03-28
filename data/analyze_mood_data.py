import os
import sys
import json
import datetime
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

def analyze_mood_trends():
    """Analyze mood trends over time"""
    print("Analyzing mood trends...")
    
    # Get all mood logs
    mood_logs = list(db.mood_logs.find().sort("timestamp", 1))
    
    if not mood_logs:
        print("No mood logs found in the database.")
        return
    
    # Count moods
    mood_counts = Counter(log['mood'] for log in mood_logs)
    
    # Group by day
    mood_by_day = defaultdict(Counter)
    for log in mood_logs:
        day = log['timestamp'].strftime('%Y-%m-%d')
        mood_by_day[day][log['mood']] += 1
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_results")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save results as JSON
    results = {
        "total_logs": len(mood_logs),
        "mood_counts": dict(mood_counts),
        "mood_by_day": {day: dict(counts) for day, counts in mood_by_day.items()},
        "analysis_time": datetime.datetime.now().isoformat()
    }
    
    with open(os.path.join(output_dir, "mood_trends.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate charts
    try:
        # Mood distribution pie chart
        plt.figure(figsize=(10, 6))
        labels = list(mood_counts.keys())
        sizes = list(mood_counts.values())
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Mood Distribution')
        plt.savefig(os.path.join(output_dir, "mood_distribution.png"))
        
        # Mood trends over time
        days = sorted(mood_by_day.keys())
        moods = sorted(set(m for day_counts in mood_by_day.values() for m in day_counts.keys()))
        
        # Only show last 14 days if there are many days
        if len(days) > 14:
            days = days[-14:]
        
        data = np.zeros((len(moods), len(days)))
        for i, mood in enumerate(moods):
            for j, day in enumerate(days):
                data[i, j] = mood_by_day[day].get(mood, 0)
        
        plt.figure(figsize=(12, 6))
        bottom = np.zeros(len(days))
        for i, mood in enumerate(moods):
            plt.bar(days, data[i], bottom=bottom, label=mood)
            bottom += data[i]
        
        plt.title('Mood Trends Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Logs')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "mood_trends.png"))
        
        print(f"Charts saved to {output_dir}")
    except Exception as e:
        print(f"Error generating charts: {e}")
    
    return results

def analyze_meal_preferences():
    """Analyze meal preferences by mood"""
    print("Analyzing meal preferences...")
    
    # Get all meals
    meals = list(db.meals.find())
    
    if not meals:
        print("No meals found in the database.")
        return
    
    # Group meals by mood tags
    meals_by_mood = defaultdict(list)
    for meal in meals:
        for mood in meal.get('mood_tags', []):
            meals_by_mood[mood].append(meal['name'])
    
    # Count meals per mood
    meal_counts_by_mood = {mood: len(meal_list) for mood, meal_list in meals_by_mood.items()}
    
    # Analyze nutritional info by mood
    nutrition_by_mood = {}
    for mood, meal_names in meals_by_mood.items():
        mood_meals = [m for m in meals if m['name'] in meal_names]
        
        if not mood_meals:
            continue
        
        # Calculate average nutritional values
        avg_calories = sum(m.get('nutritional_info', {}).get('calories', 0) for m in mood_meals) / len(mood_meals)
        avg_protein = sum(m.get('nutritional_info', {}).get('protein', 0) for m in mood_meals) / len(mood_meals)
        avg_carbs = sum(m.get('nutritional_info', {}).get('carbs', 0) for m in mood_meals) / len(mood_meals)
        avg_fat = sum(m.get('nutritional_info', {}).get('fat', 0) for m in mood_meals) / len(mood_meals)
        
        # Count dietary tags
        dietary_tags = Counter()
        for meal in mood_meals:
            for tag in meal.get('nutritional_info', {}).get('dietary_tags', []):
                dietary_tags[tag] += 1
        
        nutrition_by_mood[mood] = {
            "avg_calories": round(avg_calories, 1),
            "avg_protein": round(avg_protein, 1),
            "avg_carbs": round(avg_carbs, 1),
            "avg_fat": round(avg_fat, 1),
            "common_dietary_tags": dict(dietary_tags.most_common(3))
        }
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_results")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save results as JSON
    results = {
        "total_meals": len(meals),
        "meal_counts_by_mood": meal_counts_by_mood,
        "nutrition_by_mood": nutrition_by_mood,
        "analysis_time": datetime.datetime.now().isoformat()
    }
    
    with open(os.path.join(output_dir, "meal_preferences.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate charts
    try:
        # Meals per mood bar chart
        plt.figure(figsize=(10, 6))
        moods = list(meal_counts_by_mood.keys())
        counts = list(meal_counts_by_mood.values())
        plt.bar(moods, counts)
        plt.title('Number of Meals per Mood')
        plt.xlabel('Mood')
        plt.ylabel('Number of Meals')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "meals_per_mood.png"))
        
        # Nutritional comparison by mood
        moods = list(nutrition_by_mood.keys())
        calories = [nutrition_by_mood[mood]['avg_calories'] for mood in moods]
        protein = [nutrition_by_mood[mood]['avg_protein'] for mood in moods]
        carbs = [nutrition_by_mood[mood]['avg_carbs'] for mood in moods]
        fat = [nutrition_by_mood[mood]['avg_fat'] for mood in moods]
        
        x = np.arange(len(moods))
        width = 0.2
        
        plt.figure(figsize=(12, 6))
        plt.bar(x - width*1.5, calories, width, label='Calories (x10)')
        plt.bar(x - width/2, protein, width, label='Protein (g)')
        plt.bar(x + width/2, carbs, width, label='Carbs (g)')
        plt.bar(x + width*1.5, fat, width, label='Fat (g)')
        
        plt.title('Average Nutritional Values by Mood')
        plt.xlabel('Mood')
        plt.ylabel('Value')
        plt.xticks(x, moods, rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "nutrition_by_mood.png"))
        
        print(f"Charts saved to {output_dir}")
    except Exception as e:
        print(f"Error generating charts: {e}")
    
    return results

def analyze_user_activity():
    """Analyze user activity patterns"""
    print("Analyzing user activity...")
    
    # Get all users and their mood logs
    users = list(db.users.find())
    mood_logs = list(db.mood_logs.find())
    
    if not users or not mood_logs:
        print("No users or mood logs found in the database.")
        return
    
    # Group logs by user
    logs_by_user = defaultdict(list)
    for log in mood_logs:
        user_id = str(log['user_id'])
        logs_by_user[user_id].append(log)
    
    # Analyze user activity
    user_activity = {}
    for user in users:
        user_id = str(user['_id'])
        user_logs = logs_by_user.get(user_id, [])
        
        if not user_logs:
            continue
        
        # Count moods for this user
        mood_counts = Counter(log['mood'] for log in user_logs)
        
        # Calculate activity times
        hours = [log['timestamp'].hour for log in user_logs]
        hour_counts = Counter(hours)
        most_active_hour = hour_counts.most_common(1)[0][0] if hour_counts else None
        
        # Get first and last log dates
        if user_logs:
            first_log = min(user_logs, key=lambda x: x['timestamp'])['timestamp']
            last_log = max(user_logs, key=lambda x: x['timestamp'])['timestamp']
            days_active = (last_log - first_log).days + 1
        else:
            first_log = None
            last_log = None
            days_active = 0
        
        user_activity[user_id] = {
            "name": user.get('name', 'Anonymous'),
            "email": user.get('email', 'unknown'),
            "total_logs": len(user_logs),
            "most_common_mood": mood_counts.most_common(1)[0][0] if mood_counts else None,
            "mood_counts": dict(mood_counts),
            "most_active_hour": most_active_hour,
            "first_log": first_log.isoformat() if first_log else None,
            "last_log": last_log.isoformat() if last_log else None,
            "days_active": days_active
        }
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_results")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save results as JSON
    results = {
        "total_users": len(users),
        "active_users": len(user_activity),
        "user_activity": user_activity,
        "analysis_time": datetime.datetime.now().isoformat()
    }
    
    with open(os.path.join(output_dir, "user_activity.json"), 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"User activity analysis saved to {output_dir}/user_activity.json")
    return results

def main():
    """Main function to analyze mood data"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "=" * 70)
    print("MOODEATS DATA ANALYSIS".center(70))
    print("=" * 70 + "\n")
    
    # Check if matplotlib is installed
    try:
        import matplotlib
    except ImportError:
        print("WARNING: matplotlib is not installed. Charts will not be generated.")
        print("Install it with: pip install matplotlib numpy")
        
        # Ask if user wants to continue without charts
        confirm = input("Continue without generating charts? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled. Please install matplotlib and try again.")
            return
    
    # Run analyses
    mood_trends = analyze_mood_trends()
    meal_preferences = analyze_meal_preferences()
    user_activity = analyze_user_activity()
    
    # Create summary report
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_results")
    
    summary = {
        "analysis_time": datetime.datetime.now().isoformat(),
        "mood_trends_summary": {
            "total_logs": mood_trends["total_logs"] if mood_trends else 0,
            "most_common_mood": max(mood_trends["mood_counts"].items(), key=lambda x: x[1])[0] if mood_trends and mood_trends.get("mood_counts") else None
        },
        "meal_preferences_summary": {
            "total_meals": meal_preferences["total_meals"] if meal_preferences else 0,
            "mood_with_most_meals": max(meal_preferences["meal_counts_by_mood"].items(), key=lambda x: x[1])[0] if meal_preferences and meal_preferences.get("meal_counts_by_mood") else None
        },
        "user_activity_summary": {
            "total_users": user_activity["total_users"] if user_activity else 0,
            "active_users": user_activity["active_users"] if user_activity else 0
        }
    }
    
    with open(os.path.join(output_dir, "analysis_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETED SUCCESSFULLY".center(70))
    print(f"Results saved to: {output_dir}".center(70))
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
