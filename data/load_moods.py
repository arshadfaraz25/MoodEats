import json
import os
import sys
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

def load_sample_moods():
    """Load sample moods from JSON file"""
    print("Loading sample moods...")
    
    # Read moods from JSON file
    with open('sample_moods.json', 'r') as file:
        moods = json.load(file)
    
    # Create moods collection if it doesn't exist
    if 'moods' not in db.list_collection_names():
        db.create_collection('moods')
    else:
        # Clear existing moods
        db.moods.delete_many({})
    
    # Insert moods into database
    db.moods.insert_many(moods)
    
    print(f"Loaded {len(moods)} sample moods.")

def main():
    """Main function to load mood data"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting to load mood data...")
    load_sample_moods()
    print("Mood data loaded successfully!")

if __name__ == "__main__":
    main()
