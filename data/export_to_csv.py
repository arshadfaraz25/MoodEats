"""
File name: export_to_csv.py
Purpose: Exports MoodEats MongoDB database collections to CSV format.
         Creates a timestamped directory with CSV files for data analysis.

@author Arshad Faraz
@version 1.0.0
"""
import os
import sys
import csv
import json
import datetime
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.moodeats

# Custom JSON encoder to handle MongoDB types
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_for_csv(obj):
    """Convert MongoDB objects to CSV-compatible format"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        # For nested dictionaries, convert to JSON string
        return json.dumps(obj, cls=MongoJSONEncoder)
    elif isinstance(obj, list):
        # For lists, convert to JSON string
        return json.dumps(obj, cls=MongoJSONEncoder)
    return obj

def export_collection_to_csv(collection_name, output_dir):
    """Export a collection to a CSV file"""
    print(f"Exporting {collection_name} collection...")
    
    # Get all documents from the collection
    documents = list(db[collection_name].find())
    
    if not documents:
        print(f"No documents found in {collection_name} collection.")
        return 0
    
    # Create output filename
    filename = os.path.join(output_dir, f"{collection_name}.csv")
    
    # Get all possible fields from all documents
    all_fields = set()
    for doc in documents:
        all_fields.update(doc.keys())
    
    # Sort fields to ensure _id is first
    fields = sorted(list(all_fields))
    if '_id' in fields:
        fields.remove('_id')
        fields.insert(0, '_id')
    
    # Write to CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        
        for doc in documents:
            # Convert MongoDB-specific types
            row = {field: serialize_for_csv(doc.get(field, '')) for field in fields}
            writer.writerow(row)
    
    print(f"Exported {len(documents)} documents to {filename}")
    return len(documents)

def create_export_directory():
    """Create a directory for the export files"""
    # Create export directory with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"export_{timestamp}")
    
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    return export_dir

def create_readme(export_dir, collections_info):
    """Create a README file with export information"""
    readme_path = os.path.join(export_dir, "README.txt")
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("MoodEats Database Export\n")
        f.write("=======================\n\n")
        f.write(f"Export date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Collections exported:\n")
        for collection, count in collections_info.items():
            f.write(f"- {collection}: {count} documents\n")
        
        f.write("\nFile format: CSV (Comma Separated Values)\n")
        f.write("Encoding: UTF-8\n\n")
        
        f.write("Notes:\n")
        f.write("- ObjectId values are converted to strings\n")
        f.write("- Datetime values are in ISO format\n")
        f.write("- Nested objects and arrays are stored as JSON strings\n")
        f.write("- These files can be opened in Excel, Google Sheets, or any CSV reader\n")
        f.write("- For nested data, you may need to use JSON parsing functions\n")

def main():
    """Main function to export the database to CSV"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "=" * 70)
    print("MOODEATS DATABASE EXPORT TO CSV".center(70))
    print("=" * 70 + "\n")
    
    # Create export directory
    export_dir = create_export_directory()
    print(f"Export directory created: {export_dir}\n")
    
    # Get all collection names
    collections = db.list_collection_names()
    
    if not collections:
        print("No collections found in the database.")
        return
    
    # Export each collection
    collections_info = {}
    for collection in collections:
        count = export_collection_to_csv(collection, export_dir)
        collections_info[collection] = count
    
    # Create README file
    create_readme(export_dir, collections_info)
    
    print("\n" + "=" * 70)
    print("EXPORT COMPLETED SUCCESSFULLY".center(70))
    print(f"Total collections: {len(collections)}".center(70))
    print(f"Export location: {export_dir}".center(70))
    print("=" * 70 + "\n")
    
    print("You can now open these CSV files in Excel, Google Sheets, or any CSV reader.")

if __name__ == "__main__":
    main()
