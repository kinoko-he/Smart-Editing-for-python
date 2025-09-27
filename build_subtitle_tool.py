"""
字幕导入工具独立打包脚本
"""
import os
import subprocess
import sys

def build_subtitle_tool():
    """打包字幕导入工具为独立exe"""
    print("开始打包字幕导入工具...")
    
    # 字幕导入工具路径
    subtitle_script = os.path.join("字幕导入", "srt_subtitle_importer.py")
    
    if not os.path.exists(subtitle_script):
        print(f"错误: 未找到字幕导入工具脚本: {subtitle_script}")
        return False
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "字幕导入工具",
        "--distpath", ".",  # 输出到当前目录
        subtitle_script
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("字幕导入工具打包成功!")
            print("生成文件: 字幕导入工具.exe")
            return True
        else:
            print("打包失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"打包过程出错: {e}")
        return False

if __name__ == "__main__":
    build_subtitle_tool()
    input("按回车键退出...")