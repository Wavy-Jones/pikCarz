@echo off
REM pikCarz - Final Deployment Script
REM Run this to push everything to production!

echo.
echo ========================================
echo    PIKCARZ - FINAL DEPLOYMENT
echo ========================================
echo.

cd C:\Repos\PikCarz

echo [1/5] Checking Git status...
git status

echo.
echo [2/5] Adding all files...
git add .

echo.
echo [3/5] Committing changes...
git commit -m "PRODUCTION READY - Complete pikCarz platform with backend API, frontend integration, payments, and admin panel"

echo.
echo [4/5] Pushing to GitHub...
git push

echo.
echo [5/5] Deployment initiated!
echo.
echo ========================================
echo    DEPLOYMENT STATUS
echo ========================================
echo.
echo Frontend: Deploying to GitHub Pages...
echo Backend: Vercel will auto-deploy in ~2 mins
echo.
echo NEXT STEPS:
echo 1. Wait 3 minutes for deployments
echo 2. Visit: https://pikcarz.vercel.app
echo 3. Visit: https://wavy-jones.github.io/pikCarz
echo 4. Test registration flow
echo 5. Create test vehicle
echo.
echo ========================================
echo    ENVIRONMENT VARIABLES CHECKLIST
echo ========================================
echo.
echo Go to Vercel Dashboard and verify these are set:
echo.
echo [x] SECRET_KEY
echo [x] FRONTEND_URL
echo [x] CLOUDINARY_CLOUD_NAME
echo [x] CLOUDINARY_API_KEY
echo [x] CLOUDINARY_API_SECRET
echo [x] PAYFAST_MERCHANT_ID
echo [x] PAYFAST_MERCHANT_KEY
echo [x] PAYFAST_PASSPHRASE
echo [x] PAYFAST_MODE=sandbox
echo.
echo ========================================
echo    YOU'RE READY TO LAUNCH!
echo ========================================
echo.
echo Check MONDAY_QUICK_START.md for next steps
echo.
pause
