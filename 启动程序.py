#!/usr/bin/env python3
"""
Smart Editing 启动器
检查环境并启动主程序
"""

import sys
import subprocess
import os

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print("[错误] Python版本过低，需要3.6或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"[成功] Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """检查依赖库"""
    dependencies = ['pymiere', 'tkinter']
    missing = []
    
    for dep in dependencies:
        try:
            if dep == 'tkinter':
                import tkinter
            elif dep == 'pymiere':
                import pymiere
            print(f"[成功] {dep} 已安装")
        except ImportError:
            print(f"[缺失] {dep} 未安装")
            missing.append(dep)
    
    return missing

def install_dependencies(missing):
    """安装缺失的依赖"""
    if not missing:
        return True
    
    print(f"\n[安装] 正在安装缺失的依赖: {', '.join(missing)}")
    
    for dep in missing:
        if dep == 'tkinter':
            print("[警告] tkinter是Python标准库，如果缺失请重新安装Python")
            continue
        
        try:
            print(f"安装 {dep}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[成功] {dep} 安装成功")
            else:
                print(f"[失败] {dep} 安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"[错误] 安装 {dep} 时出错: {e}")
            return False
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("  Smart Editing - Premiere Pro 智能序列创建工具")
    print("=" * 50)
    print()
    
    print("[检查] 环境检查...")
    
    # 检查Python版本
    if not check_python_version():
        print("\n按回车键退出...")
        try:
            if hasattr(sys, 'frozen'):
                import msvcrt
                msvcrt.getch()
            else:
                input()
        except Exception:
            import time
            time.sleep(3)
        return
    
    # 检查依赖
    missing = check_dependencies()
    
    # 安装缺失依赖
    if missing:
        if not install_dependencies(missing):
            print("\n[错误] 依赖安装失败，无法启动程序")
            print("按回车键退出...")
            try:
                if hasattr(sys, 'frozen'):
                    import msvcrt
                    msvcrt.getch()
                else:
                    input()
            except Exception:
                import time
                time.sleep(3)
            return
    
    print("\n[完成] 环境检查完成")
    print("\n[提示] 使用前请确保:")
    print("1. Premiere Pro 已经启动")
    print("2. 已经打开一个项目") 
    print("3. 项目中已导入视频和音频文件")
    
    print("\n[启动] 启动程序...")
    print("-" * 50)
    
    try:
        # 导入并运行主程序
        import smart_editing
        smart_editing.main()
        
    except Exception as e:
        print(f"\n[错误] 程序运行出错: {e}")
        print("\n[解决方案]:")
        print("1. 确保Premiere Pro正在运行")
        print("2. 确保已打开一个项目")
        print("3. 尝试以管理员身份运行")
        print("4. 检查防火墙设置")
        
    finally:
        print("\n" + "=" * 50)
        print("按回车键退出...")
        try:
            # 使用不依赖stdin的方式等待用户输入
            if hasattr(sys, 'frozen'):
                # 在打包环境中使用替代方案
                import msvcrt
                msvcrt.getch()
            else:
                # 在普通Python环境中使用input
                input()
        except Exception as e:
            print(f"退出时出错: {e}")
            import time
            time.sleep(3)  # 如果出错，等待几秒后自动退出

if __name__ == "__main__":
    main()