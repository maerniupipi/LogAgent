@echo off
echo 设置 SSH 端口转发...
echo 请输入你的 DGX 服务器信息
echo.

REM 替换下面的信息为你的实际信息
set DGX_USER=your_username
set DGX_HOST=172.16.50.103
set DGX_PORT=22

echo 正在建立 SSH 隧道...
echo 本地端口 8000 -> 远程端口 8000
echo.
echo 如果提示输入密码，请输入你的 SSH 密码
echo 保持此窗口打开！关闭窗口会断开连接。
echo.

ssh -L 8000:localhost:8000 %DGX_USER%@%DGX_HOST% -p %DGX_PORT%

pause
