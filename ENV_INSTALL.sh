#!/bin/bash

# Check if pip is installed
if ! command -v pip3 > /dev/null 2>&1; then
    echo "pip3 is not installed. Installing pip3..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "requirements.txt not found in the current directory."
    exit 1
fi

# Install requirements from requirements.txt
echo "Installing requirements from requirements.txt..."
pip3 install -r requirements.txt

echo "All set up!"
