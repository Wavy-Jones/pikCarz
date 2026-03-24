@echo off
echo ============================================
echo PIKCARZ LOGIN FIX - QUICK DEPLOYMENT
echo ============================================
echo.

cd /d C:\Repos\PikCarz

echo Step 1: Opening Login Debugger...
start "" "LOGIN_DEBUGGER.html"
echo.
echo ✅ Debugger opened in your browser!
echo.
echo Watch the debugger results:
echo   - Green checkmarks = Accounts work!
echo   - Red X = Accounts have issues
echo.
pause

echo.
echo Step 2: Do you want to deploy the fixed signin page?
echo.
echo Press Y if the debugger showed GREEN checkmarks
echo Press N if accounts are still broken
echo.
set /p deploy="Deploy fixed signin page? (Y/N): "

if /i "%deploy%"=="Y" (
    echo.
    echo Deploying fixed signin page...
    
    ren signin.html signin-old-broken.html
    ren signin-fixed.html signin.html
    
    git add .
    git commit -m "Fix: Deploy improved signin page with better error handling"
    git push
    
    echo.
    echo ============================================
    echo ✅ DEPLOYMENT COMPLETE!
    echo ============================================
    echo.
    echo Wait 2-3 minutes for GitHub Pages, then test:
    echo https://pikcarz.co.za/signin.html
    echo.
) else (
    echo.
    echo ============================================
    echo Next Steps:
    echo ============================================
    echo 1. Check Vercel deployment logs
    echo 2. Verify environment variables
    echo 3. Check database has admin accounts
    echo.
    echo Read FIX_LOGIN_NOW.md for detailed instructions
    echo.
)

pause
