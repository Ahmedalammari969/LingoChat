@echo off
chcp 65001 > nul
cls
echo =======================================================
echo          LinguaChat — Real-time Multilingual Chat
echo =======================================================
echo.
echo [1/3] جاري فحص شبكات جهازك وعناوين الآي بي المتاحة...
echo.
echo =======================================================
echo  🔗 روابط الدخول المتاحة للمشروع:
echo.
echo  1. من نفس الكمبيوتر:
echo     👉 https://localhost:3000
echo.

powershell -NoProfile -Command ^
  "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' -and $_.IPAddress -notlike '169.254*' } | ForEach-Object { " ^
  "  $alias = $_.InterfaceAlias; $ip = $_.IPAddress; " ^
  "  if ($ip -like '192.168.137.*') { " ^
  "    Write-Host '  2. إذا كان أصحابك متصلين بنقطة البث (Hotspot) من جهازك:'; " ^
  "    Write-Host ('     👉 https://' + $ip + ':3000') -ForegroundColor Green; " ^
  "  } else { " ^
  "    Write-Host ('  3. إذا كنتم متصلين معاً بنفس شبكة الواي فاي (' + $alias + '):'); " ^
  "    Write-Host ('     👉 https://' + $ip + ':3000') -ForegroundColor Yellow; " ^
  "  } " ^
  "}"

echo =======================================================
echo.
echo [2/3] تشغيل خادم الباك إند (FastAPI) على المنفذ 8000...
start "LinguaChat Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --port 8000 --host 0.0.0.0"

echo [3/3] تشغيل خادم الواجهة (Vite) على المنفذ 3000...
start "LinguaChat Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ✅ تم تشغيل الخوادم بنجاح!
echo -------------------------------------------------------
pause
