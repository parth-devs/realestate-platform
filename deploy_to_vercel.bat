@echo off
cd /d "%~dp0"
echo ========================================================
echo Deploying US Real Estate Platform to Vercel (100% Free)
echo ========================================================
echo.
echo If this is your first time, Vercel will ask you to log in.
echo Just press Enter to accept the defaults!
echo.
npx vercel
echo.
echo ========================================================
echo Deployment finished! Check the URL above to view your app.
echo ========================================================
pause
