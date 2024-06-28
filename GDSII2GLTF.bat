@echo off
setlocal

:: Prompt the user for the GDS file path or name
set /p gdsfile=Enter the name of the GDS file (with extension) in the current directory or drag the file here: 

:: Remove double quotes from the file path if they exist
set gdsfile=%gdsfile:"=%

:: Determine the current directory
set currentdir=%cd%

:: Get the file name
for %%i in ("%gdsfile%") do set "filename=%%~nxi"

:: Check if the file is not in the current directory
if not exist "%currentdir%\%filename%" (
    echo File is not in the current directory. Copying to the current directory...
    copy "%gdsfile%" "%currentdir%\%filename%"
    if errorlevel 1 (
        echo Failed to copy the file. Please check the file path and try again.
        pause
        exit /b 1
    )
)

:: The file should now be in the current directory, set the path for WSL
set wslpath=%currentdir%\%filename%

:: Convert Windows path to WSL path
for /f "tokens=*" %%i in ('wsl wslpath "%wslpath%"') do set wslpath=%%i

:: Execute the Python script in WSL
wsl python3 ./thirdparty/gds2gltf.py "%wslpath%"

:: Wait for user input before closing the window
pause
