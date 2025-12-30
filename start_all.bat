@echo off
echo ========================================
echo   日志监控系统 - 启动脚本
echo ========================================
echo.

echo [1/2] 启动后端服务...
cd backend
start "日志监控后端" cmd /k "python log_api.py"
cd ..

timeout /t 3 /nobreak >nul

echo [2/2] 打开前端页面...
start "" "%CD%\frontend\log_monitor.html"

echo.
echo ========================================
echo   启动完成！
echo   后端: http://localhost:8000
echo   前端: 已在浏览器中打开
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul
