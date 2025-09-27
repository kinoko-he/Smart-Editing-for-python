@echo off
echo 启动SRT字幕导入工具测试版...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 启动测试程序
echo 启动测试程序...
python test_srt_importer.py

pause