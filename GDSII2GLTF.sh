#!/bin/bash

# Prompt the user for the GDS file path or name
read -p "Enter the name of the GDS file (with extension) in the current directory (Do Not Support Absolute Path Yet!): " gdsfile

# Remove double quotes from the file path if they exist
gdsfile=${gdsfile//\"/}

# Determine the current directory
currentdir=$(pwd)

# Get the file name
filename=$(basename "$gdsfile")

# Check if the file is not in the current directory
if [ ! -e "$currentdir/$filename" ]; then
    echo "File is not in the current directory. Copying to the current directory..."
    cp "$gdsfile" "$currentdir/$filename"
    if [ $? -ne 0 ]; then
        echo "Failed to copy the file. Please check the file path and try again."
        exit 1
    fi
fi

# The file should now be in the current directory, set the path
filepath="$currentdir/$filename"

# Execute the Python script
python3 ./thirdparty/gds2gltf.py "$filepath"

# Wait for user input before closing the window
read -p "Press any key to continue..."
