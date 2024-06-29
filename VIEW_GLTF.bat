@echo off
REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b
)

REM Check if http.server module is available
python -c "import http.server" >nul 2>&1
if %errorlevel% neq 0 (
    echo http.server module is not available. Please install Python and try again.
    exit /b
)

REM Navigate to the directory containing the HTML file
cd /d "%~dp0"

REM Start the HTTP server and redirect its output to nul
echo Starting HTTP server on port 8001...
start /b cmd /c "python -m http.server 8001 >nul 2>&1"

:main
REM Prompt the user to enter the .gltf file name
echo Please enter the .gltf file name (with extension) or drag and drop the file here, or 'q' to quit:
set /p gltf_file=

REM Check if the user wants to quit
if /i "%gltf_file%"=="q" (
    echo Exiting...
    exit /b
    exit
)

REM Remove surrounding quotes if the user dragged and dropped the file
set gltf_file=%gltf_file:"=%

REM Check if the input file exists
if not exist "%gltf_file%" (
    echo The file %gltf_file% does not exist.
    goto main
)

REM Copy the input file to view.gds.gltf
copy "%gltf_file%" "./html/view.gds.gltf" >nul
if %errorlevel% neq 0 (
    echo Failed to copy %gltf_file% to view.gds.gltf.
    goto main
)

REM Refresh the browser by opening the default browser to http://localhost:8001/html/GDS%20Viewer.html
start "" "http://localhost:8001/html/GDS%%20Viewer.html"

goto main
