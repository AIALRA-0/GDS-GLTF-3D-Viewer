#!/bin/bash

# Function to install Firefox if not installed
install_browser() {
    echo "No browser found. Installing Firefox..."
    sudo apt update
    sudo apt install -y firefox
}

# Check if the script is being run as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root or with sudo. Run it as a regular user."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python and try again."
    exit 1
fi

# Check if http.server module is available
if ! python3 -c "import http.server" &> /dev/null; then
    echo "http.server module is not available. Please install Python and try again."
    exit 1
fi

# Navigate to the directory containing the HTML file
cd "$(dirname "$0")"

# Start the HTTP server and redirect its output to /dev/null
echo "Starting HTTP server on port 8001..."
python3 -m http.server 8001 &> /dev/null &

while true; do
    # Prompt the user to enter the .gltf file name
    read -p "Please enter the .gltf file name (with extension), or 'q' to quit: " gltf_file

    # Check if the user wants to quit
    if [[ "$gltf_file" == "q" || "$gltf_file" == "Q" ]]; then
        echo "Exiting..."
        exit 0
    fi

    # Remove surrounding quotes if the user dragged and dropped the file
    gltf_file=${gltf_file//\"/}

    # Check if the input file exists
    if [[ ! -f "$gltf_file" ]]; then
        echo "The file $gltf_file does not exist."
        continue
    fi

    # Copy the input file to view.gds.gltf
    cp "$gltf_file" "./html/view.gds.gltf"
    if [[ $? -ne 0 ]]; then
        echo "Failed to copy $gltf_file to view.gds.gltf."
        continue
    fi

    # Refresh the browser by opening the default browser to http://localhost:8001/html/GDS%20Viewer.html
    if ! command -v xdg-open &> /dev/null; then
        install_browser
    fi

    # Open the browser as the current user
    xdg-open "http://localhost:8001/html/GDS%20Viewer.html"
done
