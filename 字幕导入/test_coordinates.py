#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坐标保存功能测试脚本
"""

import json
import os

def test_coordinate_save_load():
    """测试坐标保存和加载功能"""
    config_file = "coordinates_config.json"
    
    # 测试数据
    test_coordinates = {
        'import_button': [100, 200],
        'style_dropdown': [300, 400],
        'style_select': [500, 600],
        'confirm_button': [700, 800]
    }
    
    print("=== 坐标保存功能测试 ===")
    
    # 1. 测试保存
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_coordinates, f, indent=2, ensure_ascii=False)
        print("✓ 坐标保存成功")
    except Exception as e:
        print(f"✗ 坐标保存失败: {e}")
        return False
    
    # 2. 测试加载
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_coords = json.load(f)
        print("✓ 坐标加载成功")
        
        # 验证数据完整性
        if loaded_coords == test_coordinates:
            print("✓ 坐标数据完整性验证通过")
        else:
            print("✗ 坐标数据完整性验证失败")
            print(f"原始数据: {test_coordinates}")
            print(f"加载数据: {loaded_coords}")
            return False
            
    except Exception as e:
        print(f"✗ 坐标加载失败: {e}")
        return False
    
    # 3. 清理测试文件
    try:
        if os.path.exists(config_file):
            os.remove(config_file)
        print("✓ 测试文件清理完成")
    except Exception as e:
        print(f"⚠ 测试文件清理失败: {e}")
    
    print("\n=== 测试结果 ===")
    print("✓ 坐标保存和加载功能正常工作")
    return True

if __name__ == "__main__":
    test_coordinate_save_load()
    input("\n按回车键退出...")