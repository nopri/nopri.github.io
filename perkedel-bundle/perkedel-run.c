/*
perkedel-run.c
- Used in Perkedel compilers/interpreters bundle for Windows 
- (c) Noprianto <nopri.anto@icloud.com>, 2020
- Website: nopri.github.io
- License: public domain
- Compiled perkedel-run.exe runs on Windows 95 or later
*/

#include<windows.h>

int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nShowCmd)
{
    WinExec(lpCmdLine, SW_SHOW);
        
    return 0;
}


