@echo off
REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
python tcpinglib_main.py

REM Optional: pause so you can see output
pause
