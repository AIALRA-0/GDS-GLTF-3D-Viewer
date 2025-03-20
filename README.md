# GDS to GLTF Converter

This project provides a set of scripts to convert GDSII files to GLTF models and view them, inspired by the functionality of [TinyTapeout GDS Viewer](https://gds-viewer.tinytapeout.com/?model=) and [GDS2glTF](https://github.com/mbalestrini/GDS2glTF).

<p align="center">
  <img src="https://github.com/user-attachments/assets/0fe8e64f-c1f9-4bfe-b946-47070fe89892" width="800">
</p>

Special thanks to [fiumad](https://github.com/fiumad/) for providing the ideas and inspiration.

## Requirements

- A Windows environment that supports WSL (Windows Subsystem for Linux) or a Linux environment.
- Or Linux

## Installation and Usage

### Windows

1. **Run `ENV_INSTALL.bat`**:
   - This script will install WSL and the required Python environment.

2. **Run `GDSII2GLTF.bat`**:
   - Use this script to convert your `.gds` files into `.gltf` models.

3. **Run `VIEW_GLTF.bat`**:
   - This script allows you to view the `.gltf` model. Press `q` to exit the viewer.

### Linux

1. **Run `./ENV_INSTALL.sh`**:
   - This script will install the required Python environment.

2. **Run `./GDSII2GLTF.sh`**:
   - Use this script to convert your `.gds` files into `.gltf` models.

3. **Run `./VIEW_GLTF.sh`**:
   - This script allows you to view the `.gltf` model. Press `q` to exit the viewer.

By following these steps, you can easily convert and visualize your GDSII files in a GLTF format.
