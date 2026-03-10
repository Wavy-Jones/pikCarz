@echo off
echo Updating all HTML files with new logo...

REM Update about.html
powershell -Command "(Get-Content 'about.html') -replace '<div><div class=\\\"logo-text\\\">pik<span>Carz</span></div><span class=\\\"logo-sub\\\">Powered by Cubeas</span></div>', '<span class=\"logo-sub\">Powered by Cubeas</span>' | Set-Content 'about.html'"

REM Update contact.html  
powershell -Command "(Get-Content 'contact.html') -replace '<div><div class=\\\"logo-text\\\">pik<span>Carz</span></div><span class=\\\"logo-sub\\\">Powered by Cubeas</span></div>', '<span class=\"logo-sub\">Powered by Cubeas</span>' | Set-Content 'contact.html'"

REM Update dashboard.html
powershell -Command "(Get-Content 'dashboard.html') -replace '<div><div class=\\\"logo-text\\\">pik<span>Carz</span></div><span class=\\\"logo-sub\\\">Powered by Cubeas</span></div>', '<span class=\"logo-sub\">Powered by Cubeas</span>' | Set-Content 'dashboard.html'"

REM Update admin.html
powershell -Command "(Get-Content 'admin.html') -replace '<div><div class=\\\"logo-text\\\">pik<span>Carz</span></div><span class=\\\"logo-sub\\\">Powered by Cubeas</span></div>', '<span class=\"logo-sub\">Powered by Cubeas</span>' | Set-Content 'admin.html'"

echo Done! All files updated.
pause
