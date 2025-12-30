@echo off
echo ========================================
echo   日志监控系统 - 启动脚本 (Vue版本)
echo ========================================
echo.

echo [1/2] 启动后端服务...
cd backend
start "日志监控后端" cmd /k "python log_api.py"
cd ..

timeout /t 3 /nobreak >nul

echo [2/2] 启动前端开发服务器...
cd frontend
start "日志监控前端" cmd /k "npm run dev"
cd ..

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   启动完成！
echo   后端: http://localhost:8000
echo   前端: http://localhost:3000
echo ========================================
echo.
echo 正在打开浏览器...
start "" "http://localhost:3000"

echo.
echo 按任意键关闭此窗口...
pause >nul
