# GDS to GLTF Converter

This project provides a set of scripts to convert GDSII files to GLTF models and view them, inspired by the functionality of [TinyTapeout GDS Viewer](https://gds-viewer.tinytapeout.com/?model=) and [GDS2glTF](https://github.com/mbalestrini/GDS2glTF).

Special thanks to [fiumad](https://github.com/fiumad/) for providing the ideas and inspiration.

## Requirements

- A Windows environment that supports WSL (Windows Subsystem for Linux).

## Installation and Usage

1. **Run `ENV INSTALL.bat`**:
   - This script will install WSL and the required Python environment.

2. **Run `GDSII2GLTF.bat`**:
   - Use this script to convert your `.gds` files into `.gltf` models.

3. **Run `VIEW GLTF.bat`**:
   - This script allows you to view the `.gltf` model. Press `q` to exit the viewer.

## Example Usage

1. Open a terminal and navigate to the project directory.
2. Execute the installation script:
   ```bash
   ENV INSTALL.bat
   ```
3. Convert your GDS file to GLTF:
   ```bash
   GDSII2GLTF.bat your_file.gds
   ```
4. View the GLTF model:
   ```bash
   VIEW GLTF.bat your_file.gltf
   ```
5. Press `q` to quit the viewer.

By following these steps, you can easily convert and visualize your GDSII files in a GLTF format.