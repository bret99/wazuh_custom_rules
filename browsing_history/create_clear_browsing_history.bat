@echo off
C:\Windows\System32\schtasks.exe /create /tn "ClearBrowsingHistory" /tr "C:\Windows\System32\cmd.exe /c del /f /s /q ""C:\Windows\Temp\SystemInfoCollect\\*""" /sc onlogon /ru SYSTEM /rl HIGHEST /f >nul 2>&1

if %errorLevel% equ 0 (
    echo Task created successfully.
) else (
    echo Failed to create task.
)
