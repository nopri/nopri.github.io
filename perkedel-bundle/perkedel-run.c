/*
perkedel-run.c
- Used in Perkedel compilers/interpreters bundle for Windows 
- Author: Noprianto <nopri.anto@icloud.com>, 2020
- Website: nopri.github.io
- License: public domain
- Compile: gcc perkedel-run.c -mwindows -Os -s -o perkedel-run.exe
*/

#include<windows.h>

int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nShowCmd)
{
    WinExec(lpCmdLine, SW_SHOW);
        
    return 0;
}


