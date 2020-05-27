@echo off
cd temp
del program.exe 2>nul
PATH=%PATH%;..\MinGW\bin\
..\MinGW\bin\g++ code.cpp -o program.exe && program.exe
echo.
pause
