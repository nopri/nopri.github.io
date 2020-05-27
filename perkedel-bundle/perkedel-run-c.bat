@echo off
cd temp
del program.exe 2>nul
PATH=%PATH%;..\MinGW\bin\
..\MinGW\bin\gcc code.c -o program.exe && program.exe
echo.
pause
