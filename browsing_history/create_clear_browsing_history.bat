@echo off
setlocal

:: Define variables for consistency
set "TASK_NAME=ClearBrowsingHistory"
set "TARGET_DIR=%SystemRoot%\Temp\SystemInfoCollect"
set "SCHTASKS=%SystemRoot%\System32\schtasks.exe"

:: 1. Check if the task already exists
%SCHTASKS% /query /tn "%TASK_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    echo Task "%TASK_NAME%" already exists.
    exit /b 0
)

:: 2. Create the task with corrected escaping and full paths
%SCHTASKS% /create /tn "%TASK_NAME%" /tr "%SystemRoot%\System32\cmd.exe /c del /f /s /q \"%TARGET_DIR%\*\"" /sc onlogon /ru SYSTEM /rl HIGHEST /f >nul 2>&1

:: Verification
if %errorLevel% equ 0 (
    echo Task created successfully.
) else (
    echo Failed to create task.
    exit /b 1
)

endlocal
