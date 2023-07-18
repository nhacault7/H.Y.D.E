@echo off

REM Install required Python packages
pip install "rasa==3.5.10" geocoder transformers torch geopy timezonefinder sentencepiece

REM Function to check if node_modules folder exists
:check_node_modules
if not exist "hyde-web-interface\node_modules" (
    echo Node modules not found. Running 'npm install'...
    cd hyde-web-interface
    npm install --force
    cd ..
)

REM Start the action server in the background
start "" cmd /c "cd brain && rasa run actions"

:wait_for_action_server
powershell -Command "Start-Sleep -Seconds 5"
powershell -Command "(Invoke-WebRequest -Uri 'http://localhost:5055/actions' -UseBasicParsing -DisableKeepAlive).StatusCode" | findstr "200" >nul || goto wait_for_action_server

REM Start the Rasa server in a new command prompt window
start "" cmd /c "cd brain && rasa run --enable-api --cors '*'"

REM Check if node_modules folder exists and run npm install if necessary
call :check_node_modules

REM Start npm start in a new command prompt window
start "" cmd /c "cd hyde-web-interface && npm start"

