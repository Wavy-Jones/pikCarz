@echo off
echo ============================================
echo PIKCARZ EMERGENCY DEPLOYMENT
echo ============================================
echo.

cd /d C:\Repos\PikCarz

echo Checking Git status...
git status

echo.
echo Adding all files...
git add .

echo.
echo Committing changes...
git commit -m "Emergency deployment: Add password reset system, SendGrid integration, and database fixes"

echo.
echo Pushing to GitHub (will trigger Vercel deployment)...
git push

echo.
echo ============================================
echo DEPLOYMENT COMPLETE!
echo ============================================
echo.
echo Wait 2-3 minutes for Vercel to deploy, then:
echo 1. Check: https://pikcarz.vercel.app/health
echo 2. Test login at: https://pikcarz.co.za/signin.html
echo.
pause
