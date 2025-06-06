:: Turn off console printing and enable delayed expansion (change variables within for loops)
@echo off
setlocal enabledelayedexpansion

:: Default workspace directory and initialize variables for arguments passed
set "workspace=%CD%\workspace"
set "should_reset="
set "arg1="
set "arg2="

:: Parse arguments and assign variables
set "next_is_workspace_value="
for %%A in (%*) do (
    set "current_arg=%%A"
    
    if "!next_is_workspace_value!" == "1" (
        set "workspace=!current_arg!"
        set "next_is_workspace_value="
    ) else (
        :: Check for --workspace= with equals
        echo !current_arg! | find "--workspace=" >nul
        if !errorlevel! == 0 (
            set "temp_arg=!current_arg!"
            set "workspace=!temp_arg:*--workspace=!"
        ) else if "!current_arg!" == "--workspace" (
            set "next_is_workspace_value=1"
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

:: Check if workspace directory exists and make one if not
if not exist "!workspace!" (
    mkdir "!workspace!"
)

:: Reset directory if requested
if "!should_reset!"=="1" (
    set /P "confirm=Are you sure you want to delete everything in !workspace!? (y/n): "
    if /I "!confirm!" == "y" (
        del /Q "!workspace!\*"
    )
)

::Get absolute path from workspace
if not "!workspace:~1,1!" == ":" (
    set "workspace=%CD%\!workspace!"
)

:: Run Docker command with saved arguments
docker run --rm -it ^
    -p 1880:1880 -p 1883:1883 ^
    -v "!workspace!":/iqmate -w /iqmate ^
    -e IQPANEL_HOST=!arg1! -e IQPANEL_TOKEN=!arg2! ^
    suretyhome/iqmate /bin/bash

GOTO :eof

:: What is displayed if arguments are incorrect
:usage
    echo Usage: [--workspace=Path] [--reset] ^<IQ Panel Host^> ^<IQ Panel Secure Token^>
    echo.    IQ Panel Host: The hostname or IP address of the IQ Panel
    echo.    IQ Panel Secure Token: The secure token from the IQ Panel Control4 integration
    echo.    --workspace: Optionally specify path to the workspace folder (Defaults to .\workspace)
    echo.    --reset: Optionally delete contents of the workspace and start from scratch
    echo Visit https://support.suretyhome.com/t/surety-iq-mate/32721 for documentation.
    exit /b 1
