import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def main():
    print("="*50)
    print("  Premiere Pro Python工具打包程序")
    print("="*50)
    print()
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
        print("[成功] PyInstaller已安装")
    except ImportError:
        print("[错误] PyInstaller未安装，正在尝试安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 创建图标目录
    icons_dir = Path("icons")
    if not icons_dir.exists():
        icons_dir.mkdir(exist_ok=True)
        print("[创建] 已创建图标目录")
    
    # 打包选项
    print("\n请选择要打包的程序:")
    print("1. Smart Editing - 智能序列创建工具")
    print("2. 音频静音工具")
    print("3. 全部打包")
    print("4. 创建一键启动程序")
    
    choice = input("\n请输入选项 [1-4]: ")
    
    # 如果选择创建一键启动程序，直接执行不需要选择模式
    if choice == "4":
        create_launcher()
        print("\n[完成] 打包过程结束")
        input("按回车键退出...")
        return
    
    # 打包模式选项
    console_mode = True
    if choice in ["1", "2", "3"]:
        mode_choice = input("\n选择界面模式 [1-控制台模式, 2-窗口模式]: ")
        if mode_choice == "2":
            console_mode = False
    
    if choice == "1":
        package_smart_editing(console_mode)
    elif choice == "2":
        package_audio_mute(console_mode)
    elif choice == "3":
        package_smart_editing(console_mode)
        package_audio_mute(console_mode)
    else:
        print("[错误] 无效的选项")
        return
    
    print("\n[完成] 打包过程结束")
    input("按回车键退出...")

def package_smart_editing(console_mode=True):
    print("\n[开始] 打包Smart Editing - 智能序列创建工具...")
    
    # 检查是否有图标文件
    icon_path = 'icons/smart_editing.ico'
    if not os.path.exists(icon_path):
        print("[提示] 未找到图标文件，将使用默认图标")
        icon_path = 'NONE'
    
    # 创建spec文件内容
    spec_content = f'''\
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['启动程序.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pymiere', 'tkinter'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Smart Editing',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_mode},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}',
)
'''
    
    # 写入spec文件
    with open("smart_editing.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    # 执行PyInstaller
    print("[执行] PyInstaller打包中，请稍候...")
    print("[提示] 这可能需要几分钟时间，请耐心等待...")
    
    # 显示打包模式
    mode_str = "控制台模式" if console_mode else "窗口模式"
    print(f"[配置] 打包模式: {mode_str}")
    
    result = subprocess.run(["pyinstaller", "smart_editing.spec"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[成功] Smart Editing打包完成")
        print(f"[位置] 可执行文件位于: {os.path.abspath('dist/Smart Editing.exe')}")
        
        # 复制到上级目录方便访问
        try:
            output_name = "Smart Editing.exe"
            if not console_mode:
                output_name = "Smart Editing (窗口模式).exe"
                
            shutil.copy("dist/Smart Editing.exe", f"../{output_name}")
            print(f"[复制] 已复制可执行文件到: {os.path.abspath(f'../{output_name}')}")
        except Exception as e:
            print(f"[警告] 复制文件时出错: {e}")
    else:
        print("[错误] 打包失败")
        print("错误信息:")
        print(result.stderr)

def package_audio_mute(console_mode=True):
    print("\n[开始] 打包音频静音工具...")
    
    # 检查是否有图标文件
    icon_path = 'icons/audio_mute.ico'
    if not os.path.exists(icon_path):
        print("[提示] 未找到图标文件，将使用默认图标")
        icon_path = 'NONE'
    
    # 创建spec文件内容
    spec_content = f'''\
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['audio_mute_working.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pymiere'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='音频静音工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_mode},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}',
)
'''
    
    # 写入spec文件
    with open("audio_mute.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    # 执行PyInstaller
    print("[执行] PyInstaller打包中，请稍候...")
    print("[提示] 这可能需要几分钟时间，请耐心等待...")
    
    # 显示打包模式
    mode_str = "控制台模式" if console_mode else "窗口模式"
    print(f"[配置] 打包模式: {mode_str}")
    
    result = subprocess.run(["pyinstaller", "audio_mute.spec"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[成功] 音频静音工具打包完成")
        print(f"[位置] 可执行文件位于: {os.path.abspath('dist/音频静音工具.exe')}")
        
        # 复制到上级目录方便访问
        try:
            output_name = "音频静音工具.exe"
            if not console_mode:
                output_name = "音频静音工具 (窗口模式).exe"
                
            shutil.copy("dist/音频静音工具.exe", f"../{output_name}")
            print(f"[复制] 已复制可执行文件到: {os.path.abspath(f'../{output_name}')}")
        except Exception as e:
            print(f"[警告] 复制文件时出错: {e}")
    else:
        print("[错误] 打包失败")
        print("错误信息:")
        print(result.stderr)

def create_launcher():
    print("\n[开始] 创建一键启动程序...")
    
    # 创建启动器脚本
    launcher_script = '''\
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from pathlib import Path

def main():
    root = tk.Tk()
    root.title("Premiere Pro 工具集")
    root.geometry("400x300")
    root.configure(bg='#2b2b2b')
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background='#2b2b2b')
    style.configure('TButton', background='#2b2b2b', foreground='#ffffff')
    style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
    
    # 标题
    title_label = ttk.Label(root, text="Premiere Pro 工具集", font=("Arial", 16))
    title_label.pack(pady=20)
    
    # 按钮框架
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    # 按钮样式
    style.configure('TButton', font=('Arial', 12), padding=10)
    
    # 智能序列创建工具按钮
    smart_editing_btn = ttk.Button(
        button_frame, 
        text="Smart Editing - 智能序列创建工具", 
        command=lambda: run_tool("Smart Editing.exe")
    )
    smart_editing_btn.pack(pady=10, fill=tk.X, expand=True)
    
    # 音频静音工具按钮
    audio_mute_btn = ttk.Button(
        button_frame, 
        text="音频静音工具", 
        command=lambda: run_tool("音频静音工具.exe")
    )
    audio_mute_btn.pack(pady=10, fill=tk.X, expand=True)
    
    # 退出按钮
    exit_btn = ttk.Button(root, text="退出", command=root.destroy)
    exit_btn.pack(pady=20)
    
    # 状态标签
    status_label = ttk.Label(root, text="就绪", font=("Arial", 10))
    status_label.pack(side=tk.BOTTOM, pady=10)
    
    root.mainloop()

def run_tool(tool_name):
    try:
        # 获取当前脚本所在目录
        script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        tool_path = script_dir / tool_name
        
        if tool_path.exists():
            # 使用subprocess启动工具，不等待其完成
            subprocess.Popen([str(tool_path)], shell=True)
        else:
            messagebox.showerror("错误", f"找不到工具: {tool_name}\n请确保工具文件位于同一目录下。")
    except Exception as e:
        messagebox.showerror("错误", f"启动工具时出错: {e}")

if __name__ == "__main__":
    main()
'''
    
    # 写入启动器脚本
    with open("launcher.py", "w", encoding="utf-8") as f:
        f.write(launcher_script)
    
    # 检查是否有图标文件
    icon_path = 'icons/launcher.ico'
    if not os.path.exists(icon_path):
        print("[提示] 未找到启动器图标文件，将使用默认图标")
        icon_path = 'NONE'
    
    # 创建spec文件内容
    spec_content = f'''\
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Premiere Pro 工具集',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}',
)
'''
    
    # 写入spec文件
    with open("launcher.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    # 执行PyInstaller
    print("[执行] PyInstaller打包中，请稍候...")
    print("[提示] 这可能需要几分钟时间，请耐心等待...")
    
    result = subprocess.run(["pyinstaller", "launcher.spec"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[成功] 一键启动程序打包完成")
        print(f"[位置] 可执行文件位于: {os.path.abspath('dist/Premiere Pro 工具集.exe')}")
        
        # 复制到上级目录方便访问
        try:
            output_name = "Premiere Pro 工具集.exe"
            shutil.copy("dist/Premiere Pro 工具集.exe", f"../{output_name}")
            print(f"[复制] 已复制可执行文件到: {os.path.abspath(f'../{output_name}')}")
        except Exception as e:
            print(f"[警告] 复制文件时出错: {e}")
    else:
        print("[错误] 打包失败")
        print("错误信息:")
        print(result.stderr)

if __name__ == "__main__":
    main()