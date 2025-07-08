REM Prompt user for input
set /p IPADDR=Enter a value:

echo %IPADDR%


@echo off
REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
c:/Programs/ping_tester/.venv/Scripts/python.exe c:/Programs/ping_tester/tcpinglib_main.py %IPADDR%

REM Optional: pause so you can see output
pause
