@echo off
echo Fixing logo paths in all HTML files...

REM Fix index.html
powershell -Command "(Get-Content 'index.html') -replace '\"\"Logo.png\"\"', 'Logo.png' -replace '\"\"pikCarz\"\"', 'pikCarz' -replace '\"\"logo-img\"\"', 'logo-img' | Set-Content 'index.html'"

REM Fix browse.html
powershell -Command "(Get-Content 'browse.html') -replace '\"\"Logo.png\"\"', 'Logo.png' -replace '\"\"pikCarz\"\"', 'pikCarz' -replace '\"\"logo-img\"\"', 'logo-img' | Set-Content 'browse.html'"

REM Fix about.html
powershell -Command "(Get-Content 'about.html') -replace '\"\"Logo.png\"\"', 'Logo.png' -replace '\"\"pikCarz\"\"', 'pikCarz' -replace '\"\"logo-img\"\"', 'logo-img' | Set-Content 'about.html'"

REM Fix contact.html
powershell -Command "(Get-Content 'contact.html') -replace '\"\"Logo.png\"\"', 'Logo.png' -replace '\"\"pikCarz\"\"', 'pikCarz' -replace '\"\"logo-img\"\"', 'logo-img' | Set-Content 'contact.html'"

echo Done! All logos fixed.
pause
