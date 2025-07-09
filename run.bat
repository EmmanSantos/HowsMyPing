@echo off
REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
c:/Programs/ping_tester/.venv/Scripts/python.exe c:/Programs/ping_tester/main.py

REM Optional: pause so you can see output
pause
