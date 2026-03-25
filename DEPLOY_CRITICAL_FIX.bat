@echo off
echo ============================================
echo CRITICAL FIX - CORS ERROR AND PAYFAST LIVE
echo ============================================
echo.
echo ISSUES FIXED:
echo 1. ✅ FRONTEND_URL updated to pikcarz.co.za
echo 2. ✅ PayFast mode changed to LIVE
echo.
echo CODE CHANGES:
echo - backend/app/config.py updated
echo.
echo ⚠️ IMPORTANT: YOU MUST ALSO UPDATE VERCEL!
echo.
echo After this deployment, go to Vercel and:
echo 1. Update FRONTEND_URL env variable to: https://pikcarz.co.za
echo 2. Add PAYFAST_MODE env variable to: live
echo 3. Redeploy the backend
echo.
echo Without updating Vercel variables, the fix won't work!
echo.
pause

cd /d C:\Repos\PikCarz

echo.
echo Adding changes to git...
git add .

echo.
echo Committing...
git commit -m "CRITICAL FIX: Update FRONTEND_URL to pikcarz.co.za and enable PayFast live mode"

echo.
echo Pushing to GitHub...
git push

echo.
echo ============================================
echo CODE DEPLOYED TO GITHUB!
echo ============================================
echo.
echo ⚠️ NEXT STEPS - MUST DO NOW:
echo.
echo 1. Go to: https://vercel.com/dashboard
echo 2. Click: pikCarz project
echo 3. Click: Settings → Environment Variables
echo 4. Update FRONTEND_URL to: https://pikcarz.co.za
echo 5. Add PAYFAST_MODE with value: live
echo 6. Go to Deployments tab
echo 7. Click ... on latest deployment → Redeploy
echo.
echo After Vercel redeploy (2-3 min):
echo - Browse page will work ✅
echo - Motorbikes button will load ✅
echo - No more CORS errors ✅
echo - PayFast will be LIVE ✅
echo.
echo ============================================
echo.
echo Read CRITICAL_FIXES_CORS_PAYFAST.md for full details
echo.
pause
