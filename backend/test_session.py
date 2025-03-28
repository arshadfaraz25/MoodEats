import requests
import json
from pprint import pprint

# Base URL for API
BASE_URL = 'http://localhost:5000/api'

# Function to create a session and check it
def test_session():
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
        print(f"Cookies: {session.cookies.get_dict()}")
        
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
        print(f"Session Response: {session_response.text}")
    except Exception as e:
        print(f"Error checking session: {str(e)}")

# Run the test
if __name__ == "__main__":
    test_session()
