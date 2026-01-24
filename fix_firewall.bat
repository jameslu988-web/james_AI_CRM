@echo off
chcp 65001 >nul
echo ========================================
echo   CRM系统 - 防火墙一键修复工具
echo ========================================
echo.

echo 正在检查管理员权限...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [✓] 已获得管理员权限
echo.

echo 正在清理旧的防火墙规则...
netsh advfirewall firewall delete rule name="CRM Frontend Port 5173" >nul 2>&1
netsh advfirewall firewall delete rule name="CRM Backend Port 8001" >nul 2>&1
echo [✓] 旧规则已清理
echo.

echo 正在添加新的防火墙规则...
netsh advfirewall firewall add rule name="CRM Frontend Port 5173" dir=in action=allow protocol=TCP localport=5173
if %errorLevel% equ 0 (
    echo [✓] 前端端口 5173 规则添加成功
) else (
    echo [✗] 前端端口 5173 规则添加失败
)

netsh advfirewall firewall add rule name="CRM Backend Port 8001" dir=in action=allow protocol=TCP localport=8001
if %errorLevel% equ 0 (
    echo [✓] 后端端口 8001 规则添加成功
) else (
    echo [✗] 后端端口 8001 规则添加失败
)

echo.
echo ========================================
echo   防火墙配置完成！
echo ========================================
echo.
echo 当前配置：
netsh advfirewall firewall show rule name="CRM Frontend Port 5173" | findstr "已启用"
netsh advfirewall firewall show rule name="CRM Backend Port 8001" | findstr "已启用"
echo.

echo 接下来请：
echo 1. 确保前端和后端服务正在运行
echo 2. 在手机上重新点击企业微信链接测试
echo 3. 或在手机浏览器访问: http://192.168.1.110:5173
echo.

pause
