import os
import sys
import json
import datetime
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

def restore_collection(collection_name, backup_file):
    """Restore a collection from a JSON file"""
    print(f"Restoring {collection_name} collection...")
    
    # Read documents from file
    with open(backup_file, 'r') as f:
        documents = json.load(f)
    
    # Convert string IDs back to ObjectId
    for doc in documents:
        if '_id' in doc and isinstance(doc['_id'], str):
            doc['_id'] = ObjectId(doc['_id'])
        
        # Convert user_id fields to ObjectId
        if 'user_id' in doc and isinstance(doc['user_id'], str):
            doc['user_id'] = ObjectId(doc['user_id'])
        
        # Convert timestamps back to datetime objects
        for field in ['timestamp', 'created_at', 'updated_at', 'last_login']:
            if field in doc and isinstance(doc[field], str):
                try:
                    doc[field] = datetime.datetime.fromisoformat(doc[field])
                except (ValueError, TypeError):
                    pass
    
    # Clear existing collection
    db[collection_name].delete_many({})
    
    # Insert documents
    if documents:
        db[collection_name].insert_many(documents)
    
    print(f"Restored {len(documents)} documents to {collection_name} collection")
    return len(documents)

def list_backup_directories():
    """List all available backup directories"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dirs = [d for d in os.listdir(current_dir) if d.startswith('backup_') and os.path.isdir(os.path.join(current_dir, d))]
    return sorted(backup_dirs, reverse=True)  # Most recent first

def main():
    """Main function to restore the database"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "=" * 70)
    print("MOODEATS DATABASE RESTORE".center(70))
    print("=" * 70 + "\n")
    
    # List available backups
    backup_dirs = list_backup_directories()
    
    if not backup_dirs:
        print("No backup directories found. Please run backup_database.py first.")
        return
    
    print("Available backups:")
    for i, backup_dir in enumerate(backup_dirs):
        # Try to get the backup time from summary file
        summary_file = os.path.join(backup_dir, "backup_summary.json")
        backup_time = backup_dir.replace('backup_', '')
        
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
                    backup_time = summary.get('backup_time', backup_time)
            except:
                pass
        
        print(f"{i+1}. {backup_dir} - {backup_time}")
    
    # Ask user to select a backup
    while True:
        try:
            selection = int(input("\nSelect a backup to restore (number): "))
            if 1 <= selection <= len(backup_dirs):
                selected_backup = backup_dirs[selection-1]
                break
            else:
                print(f"Please enter a number between 1 and {len(backup_dirs)}")
        except ValueError:
            print("Please enter a valid number")
    
    backup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), selected_backup)
    
    print(f"\nSelected backup: {selected_backup}")
    print("WARNING: This will replace all data in your current database!")
    confirm = input("Continue? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Get all JSON files in the backup directory
    backup_files = [f for f in os.listdir(backup_path) if f.endswith('.json') and f != 'backup_summary.json']
    
    # Restore each collection
    total_documents = 0
    for backup_file in backup_files:
        collection_name = os.path.splitext(backup_file)[0]
        count = restore_collection(collection_name, os.path.join(backup_path, backup_file))
        total_documents += count
    
    print("\n" + "=" * 70)
    print("RESTORE COMPLETED SUCCESSFULLY".center(70))
    print(f"Total collections: {len(backup_files)}".center(70))
    print(f"Total documents: {total_documents}".center(70))
    print("=" * 70 + "\n")
    
    print("You can now start the MoodEats application with the restored data.")

if __name__ == "__main__":
    main()
