cd /D "%~dp0"

for %%F in (%*) do (
    python song-translate.py --infile "%%F"
)

pause
