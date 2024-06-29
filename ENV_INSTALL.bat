@echo off
setlocal

:: Check if WSL is installed
wsl --list --quiet >nul 2>&1
if errorlevel 1 (
    echo WSL is not installed. Installing WSL...
    wsl --install -d Ubuntu
    echo Please restart your computer and run this script again.
    pause
    exit /b 1
)

:: Check if WSL2 is the default version
for /f "tokens=3" %%i in ('wsl --list --verbose ^| findstr /R "Default"') do set wslVersion=%%i
if "%wslVersion%" NEQ "2" (
    echo WSL2 is not the default version. Setting WSL2 as default...
    wsl --set-default-version 2
    echo WSL2 is now set as the default version.
)

:: Ensure the default WSL distribution is Ubuntu
for /f "tokens=2 delims=:" %%i in ('wsl --list --quiet') do set defaultDistro=%%i
if /i not "%defaultDistro%"=="Ubuntu" (
    echo Setting Ubuntu as the default WSL distribution...
    wsl --set-default Ubuntu
)

:: Ensure WSL is running
wsl --set-default-version 2

:: Check if pip is installed in WSL
wsl python3 -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed. Installing pip...
    wsl sudo apt update
    wsl sudo apt install -y python3-pip
)

:: Check if requirements.txt exists
if not exist requirements.txt (
    echo requirements.txt not found in the current directory.
    pause
    exit /b 1
)

:: Install requirements from requirements.txt
echo Installing requirements from requirements.txt...
wsl python3 -m pip install -r requirements.txt

echo All set up!
pause

:: Enter WSL
wsl
