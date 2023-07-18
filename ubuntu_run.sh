#!/bin/bash

# Install required Python packages
pip install "rasa==3.5.10" geocoder transformers torch geopy timezonefinder sentencepiece

# Function to check if node_modules folder exists
check_node_modules() {
    if [ ! -d "hyde-web-interface/node_modules" ]; then
        echo "Node modules not found. Running 'npm install'..."
        (cd hyde-web-interface && npm install --force)
    fi
}

# Start the action server in the background
gnome-terminal -- bash -c "cd brain && rasa run actions"

while ! curl -s localhost:5055/actions >/dev/null; do
    sleep 5
done

# Start the Rasa server in a new terminal window
gnome-terminal -- bash -c "cd brain && rasa run --enable-api --cors '*'"

# Check if node_modules folder exists and run npm install if necessary
check_node_modules

# Start npm start in a new terminal window
gnome-terminal -- bash -c "cd hyde-web-interface && npm start"
