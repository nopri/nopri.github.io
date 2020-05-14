/*
singkong.c
- Used in Singkong.jar and Java 8 bundle, for Windows.
- (c) Noprianto <nopri.anto@icloud.com>, 2020
- Website: nopri.github.io
- License: public domain
- Compiled singkong.exe runs on Windows 95 or later
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

    char error[512];

    STARTUPINFO startup_info;
    PROCESS_INFORMATION process_info;
    
    version = GetVersion();
    major = (DWORD)(LOBYTE(LOWORD(version)));
    minor = (DWORD)(HIBYTE(LOWORD(version)));
    if (version < 0x80000000) build = (DWORD)(HIWORD(version));
    sprintf(versions, "%d.%d.%d", major, minor, build);
    
    sprintf(error, "Singkong runs wherever Java (version 5.0 or later) is available, including Windows 98 with Java 5.0. If you are using Windows and Java is not installed, this bundle might be used to run Singkong. However, bundled Java 8 requires Windows Vista or later, and this system runs Windows 95/98/Me/2000/XP/Server 2003 (%s).", versions);

    if (major < 6) {
        MessageBox(NULL, error, "Singkong", MB_OK);
    } else {
        ZeroMemory(&startup_info, sizeof(startup_info));
        startup_info.cb = sizeof(startup_info);
        ZeroMemory(&process_info, sizeof(process_info));
        GetStartupInfo (&startup_info);
        if (CreateProcess(NULL, "jre.exe -o . -y", NULL, NULL, FALSE, 0, NULL, NULL, &startup_info, &process_info)) {
            WaitForSingleObject(process_info.hProcess, INFINITE);
        }

        ZeroMemory(&startup_info, sizeof(startup_info));
        startup_info.cb = sizeof(startup_info);
        ZeroMemory(&process_info, sizeof(process_info));
        GetStartupInfo (&startup_info);
        if (CreateProcess(NULL, "jre\\bin\\javaw.exe -jar Singkong.jar", NULL, NULL, FALSE, 0, NULL, NULL, &startup_info, &process_info)) {
            WaitForSingleObject(process_info.hProcess, INFINITE);
        }
    }
    return 0;
}


