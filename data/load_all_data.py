import os
import sys
import subprocess
import time

def run_script(script_name):
    """Run a Python script and print its output"""
    print(f"\n{'=' * 50}")
    print(f"Running {script_name}...")
    print(f"{'=' * 50}\n")
    
    process = subprocess.Popen(
        [sys.executable, script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    
    # Wait for process to complete
    process.wait()
    
    # Check for errors
    if process.returncode != 0:
        print(f"Error running {script_name}. Return code: {process.returncode}")
        for line in process.stderr:
            print(line, end='')
        return False
    
    return True

def main():
    """Main function to run all data loading scripts"""
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "=" * 70)
    print("MOODEATS DATA LOADER".center(70))
    print("=" * 70 + "\n")
    
    print("This script will load all sample data for the MoodEats application.")
    print("Make sure MongoDB is running on localhost:27017 before continuing.\n")
    
    # Ask for confirmation
    confirm = input("Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Record start time
    start_time = time.time()
    
    # Run scripts in sequence
    scripts = [
        "load_sample_data.py",  # Loads meals, users, mood logs, favorites
        "load_moods.py",        # Loads mood definitions
        "generate_feedback.py"  # Generates sample feedback for meals
    ]
    
    success = True
    for script in scripts:
        if not run_script(script):
            success = False
            break
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    if success:
        print("ALL DATA LOADED SUCCESSFULLY!".center(70))
        print(f"Total time: {elapsed_time:.2f} seconds".center(70))
        print("\nYou can now start the MoodEats application and log in with:")
        print("  - Admin: admin@moodeats.com / adminpassword")
        print("  - User: john@example.com / password123")
    else:
        print("DATA LOADING FAILED".center(70))
        print("Please check the error messages above.".center(70))
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
