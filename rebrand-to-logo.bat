@echo off
REM ============================================
REM Rebrand to Official pikCarz Logo & Red Theme
REM ============================================
echo.
echo Rebranding pikCarz with official logo and bright red theme...
echo.

cd /d "%~dp0"

REM Update all HTML files - replace logo mark with actual image
powershell -Command "(Get-Content index.html) -replace '<div class=\""logo-mark\"">P</div>', '<img src=\"\"Logo.png\"\" alt=\"\"pikCarz\"\" class=\"\"logo-img\"\" />' -replace '<div class=\"\"logo-text\"">pik<span>Carz</span></div>', '' -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'style=\""color:var\(--orange\)\"\"', 'style=\""color:var(--accent)\"\"' -replace 'fill=''%%23F05A1A''', 'fill=''%%23FF4545''' -replace 'fill=''%%2300D9C0''', 'fill=''%%23FF4545''' | Set-Content index.html"

powershell -Command "(Get-Content browse.html) -replace '<div class=\""logo-mark\"">P</div>', '<img src=\"\"Logo.png\"\" alt=\"\"pikCarz\"\" class=\"\"logo-img\"\" />' -replace '<div class=\"\"logo-text\"">pik<span>Carz</span></div>', '' -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'style=\""color:var\(--orange\)\"\"', 'style=\""color:var(--accent)\"\"' -replace 'fill=''%%23F05A1A''', 'fill=''%%23FF4545''' -replace 'fill=''%%2300D9C0''', 'fill=''%%23FF4545''' | Set-Content browse.html"

powershell -Command "(Get-Content about.html) -replace '<div class=\""logo-mark\"">P</div>', '<img src=\"\"Logo.png\"\" alt=\"\"pikCarz\"\" class=\"\"logo-img\"\" />' -replace '<div class=\""logo-text\"">pik<span>Carz</span></div>', '' -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'style=\""color:var\(--orange\)\"\"', 'style=\""color:var(--accent)\"\"' -replace 'fill=''%%23F05A1A''', 'fill=''%%23FF4545''' -replace 'fill=''%%2300D9C0''', 'fill=''%%23FF4545''' | Set-Content about.html"

powershell -Command "(Get-Content contact.html) -replace '<div class=\""logo-mark\"">P</div>', '<img src=\"\"Logo.png\"\" alt=\"\"pikCarz\"\" class=\"\"logo-img\"\" />' -replace '<div class=\""logo-text\"">pik<span>Carz</span></div>', '' -replace 'text-orange', 'text-accent' -replace 'var\(--orange\)', 'var(--accent)' -replace 'style=\""color:var\(--orange\)\"\"', 'style=\""color:var(--accent)\"\"' -replace 'fill=''%%23F05A1A''', 'fill=''%%23FF4545''' -replace 'fill=''%%2300D9C0''', 'fill=''%%23FF4545''' | Set-Content contact.html"

echo.
echo Done! All files updated with official logo and red theme.
echo.
echo IMPORTANT: Make sure Logo.png is in the project root folder!
echo.
echo Press any key to close...
pause >nul
