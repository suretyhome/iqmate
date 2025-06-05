:: Turn off console printing and enable delayed expansion (change variables within for loops)
@echo off
setlocal enabledelayedexpansion

:: Default shared directory and initialize variables for arguments passed
set "shared_dir=%CD%\shared"
set "should_reset="
set "arg1="
set "arg2="

:: Parse arguments and assign variables
set "next_is_shared_value="
for %%A in (%*) do (
    set "current_arg=%%A"
    
    if "!next_is_shared_value!" == "1" (
        set "shared_dir=!current_arg!"
        set "next_is_shared_value="
    ) else (
        :: Check for --shared= with equals
        echo !current_arg! | find "--shared=" >nul
        if !errorlevel! == 0 (
            set "temp_arg=!current_arg!"
            set "shared_dir=!temp_arg:*--shared=!"
        ) else if "!current_arg!" == "--shared" (
            set "next_is_shared_value=1"
        ) else if "!current_arg!" == "--reset" (
            set "should_reset=1"
        ) else (
            if "!arg1!" == "" (
                set "arg1=%%A"
            ) else if "!arg2!" == "" (
                set "arg2=%%A"
            )
        )
    )
)

:: Check if arguments (Host IP and Secure Token in that order) were found. If not => usage
if "!arg1!"=="" GOTO :usage
if "!arg2!"=="" GOTO :usage

:: Check if shared directory exists and make one if not
if not exist "!shared_dir!" (
    mkdir "!shared_dir!"
)

:: Reset directory if requested
if "!should_reset!"=="1" (
    set /P "confirm=Are you sure you want to delete everything in !shared_dir!? (y/n): "
    if /I "!confirm!" == "y" (
        del /Q "!shared_dir!\*"
    )
)

::Get absolute path from shared_dir
if not "!shared_dir:~1,1!" == ":" (
    set "shared_dir=%CD%\!shared_dir!"
)

:: Run Docker command with saved arguments
docker run --rm -it ^
    -p 1880:1880 -p 1883:1883 ^
    -v "!shared_dir!":/iqmate -w /iqmate ^
    -e IQPANEL_HOST=!arg1! -e IQPANEL_TOKEN=!arg2! ^
    suretyhome/iqmate /bin/bash

GOTO :eof

:: What is displayed if arguments are incorrect
:usage
    echo Usage: [--shared=Path] [--reset] ^<IQ Panel Host^> ^<IQ Panel Secure Token^>
    echo.    IQ Panel Host: The hostname or IP address of the IQ Panel
    echo.    IQ Panel Secure Token: The secure token from the IQ Panel Control4 integration
    echo.    --shared: Optionally specify path to the shared directory (Defaults to .\shared)
    echo.    --reset: Optionally delete contents of shared directory and start from scratch
    echo Visit https://support.suretyhome.com/t/surety-iq-mate/32721 for documentation.
    exit /b 1
