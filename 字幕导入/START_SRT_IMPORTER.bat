@echo off
echo 启动SRT字幕自动导入工具...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 尝试安装依赖
echo 检查并安装依赖库...
pip install -r requirements.txt

REM 启动程序
echo 启动程序...
python srt_subtitle_importer.py

pause