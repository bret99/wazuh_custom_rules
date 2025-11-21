Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c C:\Windows\systeminfocollect.bat", 0, False
Set WshShell = Nothing
