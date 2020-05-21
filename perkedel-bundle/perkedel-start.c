/*
perkedel-start.c
- Used in Perkedel compilers/interpreters bundle for Windows 
- (c) Noprianto <nopri.anto@icloud.com>, 2020
- Website: nopri.github.io
- License: public domain
- Compiled perkedel-start.exe runs on Windows 95 or later
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

    char *drive;

    char error[255];

    char path[16];
    char confirm[255];
    char extract[64];
    char run[64];
    char dir[16];

    STARTUPINFO startup_info;
    PROCESS_INFORMATION process_info;
    
    version = GetVersion();
    major = (DWORD)(LOBYTE(LOWORD(version)));
    minor = (DWORD)(HIBYTE(LOWORD(version)));
    if (version < 0x80000000) build = (DWORD)(HIWORD(version));
    sprintf(versions, "%d.%d.%d", major, minor, build);

    drive = getenv("SystemDrive");
    sprintf(path, "%s\\perkedel", drive);
    
    sprintf(error, "Perkedel uses Java 8 and requires Windows Vista or later. This system runs Windows 95/98/Me/2000/XP/Server 2003 (%s).", versions);
    sprintf(confirm, "Do you want to copy Perkedel to %s? If no is selected, perkedel will be run in a temporary directory (automatically clean up).", path);

    if (major < 6) {
        MessageBox(NULL, error, "Perkedel", MB_OK);
    } else {
        int res = MessageBox(NULL, confirm, "Perkedel", MB_YESNO);
        if (res == IDYES) {
            sprintf(extract, "perkedel-bundle.exe -o\"%s\" -y", path);
            sprintf(run, "%s\\perkedel.exe", path);
            sprintf(dir, "%s\\", path);
        } else {
            sprintf(extract, "perkedel-bundle.exe -o . -y");
            sprintf(run, "perkedel.exe", path);
            sprintf(dir, ".");
        }
        
        ZeroMemory(&startup_info, sizeof(startup_info));
        startup_info.cb = sizeof(startup_info);
        ZeroMemory(&process_info, sizeof(process_info));
        GetStartupInfo (&startup_info);
        if (CreateProcess(NULL, extract, NULL, NULL, FALSE, 0, NULL, NULL, &startup_info, &process_info)) {
            WaitForSingleObject(process_info.hProcess, INFINITE);
        }

        SetCurrentDirectory(dir);
        ZeroMemory(&startup_info, sizeof(startup_info));
        startup_info.cb = sizeof(startup_info);
        ZeroMemory(&process_info, sizeof(process_info));
        GetStartupInfo (&startup_info);
        if (CreateProcess(NULL, run, NULL, NULL, FALSE, 0, NULL, NULL, &startup_info, &process_info)) {
            WaitForSingleObject(process_info.hProcess, INFINITE);
        }
    }
    return 0;
}


