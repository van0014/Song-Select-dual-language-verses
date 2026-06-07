@echo off
cd /D "%~dp0"

:loop
if "%~1"=="" goto end

python song-translate.py --infile "%~1"

shift
goto loop

:end
pause
