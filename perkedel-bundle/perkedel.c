/*
perkedel.c
- Used in Perkedel compilers/interpreters bundle for Windows 
- Author: Noprianto <nopri.anto@icloud.com>, 2020
- Website: nopri.github.io
- License: public domain
- Compile: gcc perkedel.c -mwindows -Os -s -o perkedel.exe
*/

#include<stdio.h>
#include<windows.h>

int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nShowCmd)
{
    DWORD version = 0;
    DWORD major = 0;
    DWORD minor = 0;
    DWORD build = 0;
    char versions[32];

    char error[255];

    STARTUPINFO startup_info;
    PROCESS_INFORMATION process_info;
    
    version = GetVersion();
    major = (DWORD)(LOBYTE(LOWORD(version)));
    minor = (DWORD)(HIBYTE(LOWORD(version)));
    if (version < 0x80000000) build = (DWORD)(HIWORD(version));
    sprintf(versions, "%d.%d.%d", major, minor, build);
    
    sprintf(error, "Perkedel uses Java 8 and requires Windows Vista or later. This system runs Windows 95/98/Me/2000/XP/Server 2003 (%s).", versions);

    if (major < 6) {
        MessageBox(NULL, error, "Perkedel", MB_OK);
    } else {
        ZeroMemory(&startup_info, sizeof(startup_info));
        startup_info.cb = sizeof(startup_info);
        ZeroMemory(&process_info, sizeof(process_info));
        GetStartupInfo (&startup_info);
        if (CreateProcess(NULL, "cmd.exe /C perkedel\\perkedel-new-singkong.bat", NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &startup_info, &process_info)) {
            WaitForSingleObject(process_info.hProcess, INFINITE);
        }

        ZeroMemory(&startup_info, sizeof(startup_info));
        startup_info.cb = sizeof(startup_info);
        ZeroMemory(&process_info, sizeof(process_info));
        GetStartupInfo (&startup_info);
        if (CreateProcess(NULL, "jre\\bin\\javaw.exe -jar Singkong.jar perkedel\\perkedel.singkong", NULL, NULL, FALSE, 0, NULL, NULL, &startup_info, &process_info)) {
            WaitForSingleObject(process_info.hProcess, INFINITE);
        }
    }
    return 0;
}


