import requests
import json
from pprint import pprint

# Base URL for API
BASE_URL = 'http://localhost:5000/api'

# Function to create a session and log in
def login_and_test_favorites():
    session = requests.Session()
    
    # Step 1: Login
    print("Step 1: Logging in...")
    login_data = {
        "email": "test@gmail.com",
        "password": "password123"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/users/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")
        
        if login_response.status_code != 200:
            print("Login failed. Cannot proceed with tests.")
            return
            
        print("\nLogin successful!")
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return
    
    # Step 2: Check session
    print("\nStep 2: Checking session...")
    try:
        session_response = session.get(f"{BASE_URL}/users/check-session")
        print(f"Session Status: {session_response.status_code}")
        print(f"Session Response: {json.dumps(session_response.json(), indent=2)}")
    except Exception as e:
        print(f"Error checking session: {str(e)}")
    
    # Step 3: Get favorites
    print("\nStep 3: Getting favorites...")
    try:
        favorites_response = session.get(f"{BASE_URL}/users/favorites")
        print(f"Favorites Status: {favorites_response.status_code}")
        
        if favorites_response.status_code == 200:
            favorites_data = favorites_response.json()
            print(f"Favorites count: {len(favorites_data)}")
            if len(favorites_data) > 0:
                print("First favorite meal:")
                pprint(favorites_data[0])
            else:
                print("No favorites found.")
        else:
            print(f"Error response: {favorites_response.text}")
    except Exception as e:
        print(f"Error getting favorites: {str(e)}")
    
    # Step 4: Add a favorite
    print("\nStep 4: Adding a favorite...")
    try:
        # Get a meal ID to add as favorite
        meals_response = session.get(f"{BASE_URL}/meals?limit=1")
        if meals_response.status_code == 200:
            meals = meals_response.json()
            if len(meals) > 0:
                meal_id = meals[0]["_id"]
                print(f"Adding meal {meal_id} to favorites...")
                
                add_response = session.post(f"{BASE_URL}/users/favorites/{meal_id}")
                print(f"Add Favorite Status: {add_response.status_code}")
                print(f"Add Favorite Response: {add_response.text}")
                
                # Check favorites again
                print("\nChecking favorites after adding...")
                favorites_response = session.get(f"{BASE_URL}/users/favorites")
                print(f"Favorites Status: {favorites_response.status_code}")
                
                if favorites_response.status_code == 200:
                    favorites_data = favorites_response.json()
                    print(f"Favorites count: {len(favorites_data)}")
                    if len(favorites_data) > 0:
                        print("First favorite meal:")
                        pprint(favorites_data[0])
                    else:
                        print("No favorites found.")
            else:
                print("No meals found to add as favorite.")
        else:
            print(f"Error getting meals: {meals_response.text}")
    except Exception as e:
        print(f"Error adding favorite: {str(e)}")

# Run the test
if __name__ == "__main__":
    login_and_test_favorites()
