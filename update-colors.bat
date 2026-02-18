@echo off
REM ============================================
REM Color Update Script - Orange to Teal
REM ============================================
echo.
echo Updating color references in HTML files...
echo.

cd /d "%~dp0"

powershell -Command "(Get-Content index.html) -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'fill=''%%23F05A1A''', 'fill=''%%2300D9C0''' | Set-Content index.html"
powershell -Command "(Get-Content browse.html) -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'fill=''%%23F05A1A''', 'fill=''%%2300D9C0''' | Set-Content browse.html"
powershell -Command "(Get-Content about.html) -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'fill=''%%23F05A1A''', 'fill=''%%2300D9C0''' | Set-Content about.html"
powershell -Command "(Get-Content contact.html) -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'fill=''%%23F05A1A''', 'fill=''%%2300D9C0''' | Set-Content contact.html"

echo.
echo Done! All HTML files updated to teal theme.
echo.
echo Press any key to close...
pause >nul
