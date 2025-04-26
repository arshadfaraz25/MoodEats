"""
File name: backup_database.py
Purpose: Creates a backup of the MoodEats MongoDB database.
         Exports all collections to JSON files in a timestamped directory.

@author Arshad Faraz
@version 1.0.0
"""
import os
import sys
import subprocess
import datetime
import json
from pymongo import MongoClient
from bson import ObjectId, datetime as bson_datetime

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB-specific types"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, (datetime.datetime, bson_datetime.datetime)):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)

def backup_collection(collection_name, output_dir):
    """Backup a collection to a JSON file"""
    print(f"Backing up {collection_name} collection...")
    
    # Get all documents from the collection
    documents = list(db[collection_name].find())
    
    # Create output filename
    filename = os.path.join(output_dir, f"{collection_name}.json")
    
    # Write to file
    with open(filename, 'w') as f:
        json.dump(documents, f, cls=JSONEncoder, indent=2)
    
    print(f"Saved {len(documents)} documents to {filename}")
    return len(documents)

def create_backup_directory():
    """Create a directory for the backup files"""
    # Create backup directory with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"backup_{timestamp}")
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    return backup_dir

def main():
    """Main function to backup the database"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "=" * 70)
    print("MOODEATS DATABASE BACKUP".center(70))
    print("=" * 70 + "\n")
    
    # Create backup directory
    backup_dir = create_backup_directory()
    print(f"Backup directory created: {backup_dir}\n")
    
    # Get all collection names
    collections = db.list_collection_names()
    
    # Backup each collection
    total_documents = 0
    for collection in collections:
        count = backup_collection(collection, backup_dir)
        total_documents += count
    
    # Create a summary file
    summary = {
        "backup_time": datetime.datetime.now().isoformat(),
        "collections": collections,
        "total_documents": total_documents
    }
    
    with open(os.path.join(backup_dir, "backup_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 70)
    print("BACKUP COMPLETED SUCCESSFULLY".center(70))
    print(f"Total collections: {len(collections)}".center(70))
    print(f"Total documents: {total_documents}".center(70))
    print(f"Backup location: {backup_dir}".center(70))
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
