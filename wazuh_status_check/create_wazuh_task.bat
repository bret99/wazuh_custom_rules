@echo off
setlocal

:: Task parameters
set TASK_NAME="Wazuh Service Monitor"
set TASK_DESCRIPTION="WazuhSvc check and running every 5 minutes"
set TASK_COMMAND="cmd.exe /c sc query WazuhSvc | find \"RUNNING\" >nul 2>&1 || net start WazuhSvc"

:: Creating task in Task Scheduler
echo Creating scheduled task...

schtasks /create /tn %TASK_NAME% /tr %TASK_COMMAND% /sc minute /mo 5 /ru SYSTEM /f

if %errorlevel% equ 0 (
    echo.
    echo Task created successfully!
    echo Task name: %TASK_NAME%
    echo Running every 5 minutes
    echo Running from: SYSTEM
) else (
    echo.
    echo Task craetion ERROR!
    echo Check Administratot rights
)

endlocal
pause
