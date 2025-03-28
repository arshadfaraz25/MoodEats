@echo off
echo ===================================================
echo MoodEats Database Setup
echo ===================================================
echo.
echo This script will set up the MoodEats database with sample data.
echo.
echo Options:
echo 1. Load all sample data (meals, users, moods, feedback)
echo 2. Load only mood definitions
echo 3. Generate sample feedback for meals
echo 4. Backup current database
echo 5. Analyze mood data
echo 6. Exit
echo.

:menu
set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto load_all
if "%choice%"=="2" goto load_moods
if "%choice%"=="3" goto generate_feedback
if "%choice%"=="4" goto backup_db
if "%choice%"=="5" goto analyze_data
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
goto menu

:load_all
echo.
echo Loading all sample data...
python load_all_data.py
echo.
pause
goto menu

:load_moods
echo.
echo Loading mood definitions...
python load_moods.py
echo.
pause
goto menu

:generate_feedback
echo.
echo Generating sample feedback...
python generate_feedback.py
echo.
pause
goto menu

:backup_db
echo.
echo Backing up database...
python backup_database.py
echo.
pause
goto menu

:analyze_data
echo.
echo Analyzing mood data...
python analyze_mood_data.py
echo.
pause
goto menu

:end
echo.
echo Thank you for using MoodEats Database Setup!
echo.
