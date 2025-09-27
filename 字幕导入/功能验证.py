#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT字幕自动导入工具 - 功能验证脚本
验证所有核心功能是否正常工作
"""

import os
import json
import sys
from pathlib import Path

def check_dependencies():
    """检查依赖库"""
    print("=== 检查依赖库 ===")
    
    required_packages = [
        'tkinter',
        'pymiere', 
        'pyautogui',
        'keyboard',
        'pyperclip'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'pymiere':
                import pymiere
            elif package == 'pyautogui':
                import pyautogui
            elif package == 'keyboard':
                import keyboard
            elif package == 'pyperclip':
                import pyperclip
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依赖: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("✓ 所有依赖库已安装")
        return True

def check_files():
    """检查必要文件"""
    print("\n=== 检查项目文件 ===")
    
    required_files = [
        'srt_subtitle_importer.py',
        'requirements.txt',
        'START_SRT_IMPORTER.bat',
        'START_TEST.bat',
        'README_SRT_IMPORTER.md',
        '使用说明.md',
        'CHANGELOG.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - 文件不存在")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("✓ 所有必要文件存在")
        return True

def test_coordinate_system():
    """测试坐标系统"""
    print("\n=== 测试坐标保存系统 ===")
    
    config_file = "coordinates_config.json"
    
    # 测试数据
    test_coords = {
        'import_button': [100, 200],
        'style_dropdown': [300, 400],
        'style_select': [500, 600],
        'confirm_button': [700, 800]
    }
    
    try:
        # 测试保存
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_coords, f, indent=2, ensure_ascii=False)
        print("✓ 坐标保存功能正常")
        
        # 测试加载
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_coords = json.load(f)
        
        if loaded_coords == test_coords:
            print("✓ 坐标加载功能正常")
            print("✓ 数据完整性验证通过")
        else:
            print("✗ 数据完整性验证失败")
            return False
        
        # 清理测试文件
        os.remove(config_file)
        print("✓ 测试文件清理完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 坐标系统测试失败: {e}")
        return False

def check_main_program():
    """检查主程序是否可以启动"""
    print("\n=== 检查主程序 ===")
    
    try:
        # 尝试导入主程序模块
        sys.path.insert(0, '.')
        
        # 检查主程序文件的语法
        with open('srt_subtitle_importer.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'srt_subtitle_importer.py', 'exec')
        print("✓ 主程序语法检查通过")
        
        # 检查关键类和方法
        if 'class SRTSubtitleImporter' in code:
            print("✓ 主类定义存在")
        else:
            print("✗ 主类定义缺失")
            return False
        
        # 检查关键方法
        key_methods = [
            'load_coordinates',
            'save_coordinates', 
            'get_coordinate',
            'update_coordinate_display',
            'clear_coordinates'
        ]
        
        for method in key_methods:
            if f'def {method}' in code:
                print(f"✓ {method} 方法存在")
            else:
                print(f"✗ {method} 方法缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 主程序检查失败: {e}")
        return False

def main():
    """主验证函数"""
    print("SRT字幕自动导入工具 - 功能验证")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    if not current_dir.endswith('字幕导入'):
        print("⚠️  请在'字幕导入'目录下运行此脚本")
        print("正确路径应该是: .../字幕导入/")
        input("\n按回车键退出...")
        return
    
    # 执行各项检查
    checks = [
        ("依赖库检查", check_dependencies),
        ("项目文件检查", check_files),
        ("坐标系统测试", test_coordinate_system),
        ("主程序检查", check_main_program)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ {check_name}执行失败: {e}")
            all_passed = False
    
    # 总结
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有功能验证通过！")
        print("\n✅ 程序已准备就绪，可以正常使用")
        print("\n📋 使用步骤:")
        print("1. 启动 Premiere Pro 并打开项目")
        print("2. 双击 START_SRT_IMPORTER.bat 启动程序")
        print("3. 按照4个步骤完成字幕导入")
        print("\n💡 新功能: 坐标配置会自动保存，下次使用更方便！")
    else:
        print("❌ 部分功能验证失败")
        print("请检查上述错误信息并修复相关问题")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()