@echo off
cd /D "%~dp0"

:: 1. If no file is dragged and dropped, go to the folder traversal block
if "%~1"=="" goto no_input

:: 2. Process all dragged-and-dropped files
for %%I in (%*) do (
    echo "%%~nxI" | findstr /I "_ZH-HANS" >nul && (
        echo Skipping already translated file: %%~nxI
    ) || (
        python song-translate.py --infile "%%~fI"
    )
)
goto end

:no_input
echo No input file provided. Processing all .txt files in directory...
for %%F in (*.txt) do (
    echo "%%~nxF" | findstr /I "_ZH-HANS" >nul && (
        rem Do nothing, this file is skipped
    ) || (
        python song-translate.py --infile "%%~fF"
    )
)

:end
pause
