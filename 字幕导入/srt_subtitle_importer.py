"""
SRT字幕自动导入工具 - Premiere Pro 字幕导入自动化
基于pymiere API和自动化控制实现SRT字幕文件自动导入
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import re
import threading
import time
import sys
import traceback
from pathlib import Path
import pyautogui
import keyboard
from collections import defaultdict
import json

# 尝试导入pymiere，如果失败则提供错误信息
try:
    import pymiere
    pymiere_available = True
    pymiere_error = None
except ImportError as e:
    pymiere_available = False
    pymiere_error = str(e)
except Exception as e:
    pymiere_available = False
    pymiere_error = str(e)

class SRTSubtitleImporter:
    def __init__(self, root):
        self.root = root
        self.app = None
        self.project = None
        self.srt_directory = ""
        self.srt_files = []
        self.matched_files = []
        
        # 坐标配置文件路径
        self.config_file = os.path.join(os.path.dirname(__file__), 'coordinates_config.json')
        
        # 坐标配置
        self.coordinates = {
            'import_button': None,      # 坐标1: 文件导入按钮
            'style_dropdown': None,     # 坐标2: 字幕样式下拉菜单
            'style_select': None,       # 坐标3: 字幕样式选择
            'confirm_button': None      # 坐标4: 确定按钮
        }
        
        # 初始化UI组件变量
        self.connection_label = None
        self.notebook = None
        self.dir_var = None
        self.dir_entry = None
        self.browse_button = None
        self.match_tree = None
        self.coord_labels = {}
        self.test_coords_button = None
        self.coord_status_label = None
        self.execute_button = None
        self.stop_button = None
        self.import_status_text = None
        self.import_running = False
        self.import_thread = None
        self.hotkey_thread = None
        self.progress_var = None
        self.progress_bar = None
        self.log_text = None
        
        self.setup_ui()
        
        # 加载保存的坐标配置（在UI创建后）
        self.load_coordinates()
        
        # 更新坐标显示
        self.update_coordinate_display()
        
        # 延迟连接，避免启动时卡顿
        self.root.after(1000, self.connect_to_premiere)
    
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("SRT字幕自动导入工具 - Premiere Pro")
        self.root.geometry("700x600")
        self.root.configure(bg='#2b2b2b')  # 深色主题
        
        # 设置样式
        try:
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Dark.TFrame', background='#2b2b2b')
            style.configure('Dark.TLabel', background='#2b2b2b', foreground='#ffffff')
            style.configure('Dark.TButton', background='#404040', foreground='#ffffff')
            style.map('Dark.TButton', background=[('active', '#505050')])
            
            # 配置复选框样式
            style.configure('Dark.TCheckbutton', 
                          background='#2b2b2b', 
                          foreground='#ffffff',
                          focuscolor='none')
            style.map('Dark.TCheckbutton',
                     background=[('active', '#2b2b2b')],
                     foreground=[('active', '#ffffff')])
        except Exception as e:
            print(f"样式设置失败: {e}")
        
        # 主框架
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="SRT字幕自动导入工具", 
                               font=('Arial', 18, 'bold'), style='Dark.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Premiere Pro 字幕导入自动化 v1.0", 
                                  font=('Arial', 10), style='Dark.TLabel')
        subtitle_label.pack()
        
        # 连接状态
        self.status_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        if not pymiere_available:
            self.connection_label = ttk.Label(self.status_frame, 
                                             text="错误: pymiere库未安装", 
                                             style='Dark.TLabel')
        else:
            self.connection_label = ttk.Label(self.status_frame, 
                                             text="正在连接 Premiere Pro...", 
                                             style='Dark.TLabel')
        self.connection_label.pack()
        
        # 创建Notebook用于分步骤界面
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 步骤1: 文件扫描和匹配
        self.setup_step1_frame()
        
        # 步骤2: 坐标配置
        self.setup_step2_frame()
        
        # 步骤3: 执行导入
        self.setup_step3_frame()
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, 
                                          variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 状态反馈区域
        status_label = ttk.Label(main_frame, text="处理日志:", style='Dark.TLabel')
        status_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(main_frame, 
                                                 height=8,
                                                 bg='#1e1e1e',
                                                 fg='#ffffff',
                                                 insertbackground='#ffffff')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 如果pymiere不可用，显示错误信息
        if not pymiere_available:
            self.log(f"错误: pymiere库未安装 - {pymiere_error}")
            self.log("请运行: pip install pymiere")
    
    def setup_step1_frame(self):
        """步骤1: 文件扫描和匹配界面"""
        step1_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(step1_frame, text="步骤1: 文件扫描和匹配")
        
        # 目录选择
        dir_frame = ttk.Frame(step1_frame, style='Dark.TFrame')
        dir_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(dir_frame, text="SRT文件目录:", style='Dark.TLabel').pack(anchor=tk.W)
        
        dir_select_frame = ttk.Frame(dir_frame, style='Dark.TFrame')
        dir_select_frame.pack(fill=tk.X, pady=5)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_select_frame, textvariable=self.dir_var, width=60)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(dir_select_frame, text="浏览", 
                                       command=self.browse_and_match, style='Dark.TButton')
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 匹配结果
        ttk.Label(dir_frame, text="匹配结果:", style='Dark.TLabel').pack(anchor=tk.W, pady=(20, 0))
        
        # 创建Treeview显示匹配结果
        columns = ('序列名', 'SRT文件', '匹配数字')
        self.match_tree = ttk.Treeview(dir_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.match_tree.heading(col, text=col)
            self.match_tree.column(col, width=150)
        
        self.match_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(dir_frame, orient=tk.VERTICAL, command=self.match_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.match_tree.configure(yscrollcommand=scrollbar.set)
    
    def setup_step2_frame(self):
        """步骤2: 坐标配置界面"""
        step2_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(step2_frame, text="步骤2: 坐标配置")
        
        # 说明文字
        info_label = ttk.Label(step2_frame, 
                              text="请按顺序配置以下按钮坐标。点击'获取坐标'后，按F1键确定鼠标位置。", 
                              style='Dark.TLabel', wraplength=600)
        info_label.pack(pady=10)
        
        # 坐标配置区域
        coord_frame = ttk.Frame(step2_frame, style='Dark.TFrame')
        coord_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 坐标配置项
        coord_configs = [
            ('坐标1: 文件导入按钮', 'import_button'),
            ('坐标2: 字幕样式下拉菜单', 'style_dropdown'),
            ('坐标3: 字幕样式选择', 'style_select'),
            ('坐标4: 确定按钮', 'confirm_button')
        ]
        
        self.coord_labels = {}
        
        for i, (label_text, coord_key) in enumerate(coord_configs):
            frame = ttk.Frame(coord_frame, style='Dark.TFrame')
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label_text, style='Dark.TLabel', width=25).pack(side=tk.LEFT)
            
            coord_label = ttk.Label(frame, text="未设置", style='Dark.TLabel', width=15)
            coord_label.pack(side=tk.LEFT, padx=10)
            self.coord_labels[coord_key] = coord_label
            
            get_coord_btn = ttk.Button(frame, text="获取坐标", 
                                      command=lambda key=coord_key: self.get_coordinate(key),
                                      style='Dark.TButton')
            get_coord_btn.pack(side=tk.RIGHT)
        
        # 测试坐标按钮
        test_frame = ttk.Frame(step2_frame, style='Dark.TFrame')
        test_frame.pack(fill=tk.X, pady=20)
        
        self.test_coords_button = ttk.Button(test_frame, text="测试所有坐标", 
                                           command=self.test_coordinates, style='Dark.TButton')
        self.test_coords_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清除坐标按钮
        clear_coords_button = ttk.Button(test_frame, text="清除所有坐标", 
                                        command=self.clear_coordinates, style='Dark.TButton')
        clear_coords_button.pack(side=tk.LEFT)
        
        # 坐标状态提示
        coord_status_frame = ttk.Frame(step2_frame, style='Dark.TFrame')
        coord_status_frame.pack(fill=tk.X, pady=10)
        
        self.coord_status_label = ttk.Label(coord_status_frame, 
                                           text="", 
                                           style='Dark.TLabel', 
                                           font=('Arial', 9))
        self.coord_status_label.pack()
    
    def setup_step3_frame(self):
        """步骤3: 执行导入界面"""
        step3_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(step3_frame, text="步骤3: 执行导入")
        
        # 执行选项
        options_frame = ttk.Frame(step3_frame, style='Dark.TFrame')
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(options_frame, text="导入选项:", style='Dark.TLabel').pack(anchor=tk.W)
        
        info_label = ttk.Label(options_frame, 
                              text="程序将按数字顺序自动导入SRT字幕文件到对应序列", 
                              style='Dark.TLabel', wraplength=500)
        info_label.pack(anchor=tk.W, pady=5)
        
        # 快捷键提示
        hotkey_label = ttk.Label(options_frame, 
                                text="💡 提示：导入过程中按 ESC 键可快速停止", 
                                style='Dark.TLabel', wraplength=500,
                                font=('Arial', 9))
        hotkey_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 执行按钮
        execute_frame = ttk.Frame(step3_frame, style='Dark.TFrame')
        execute_frame.pack(fill=tk.X, pady=20)
        
        self.execute_button = ttk.Button(execute_frame, text="开始自动导入", 
                                        command=self.start_import_process, 
                                        style='Dark.TButton')
        self.execute_button.pack()
        
        # 停止按钮
        self.stop_button = ttk.Button(execute_frame, text="停止导入", 
                                     command=self.stop_import_process, 
                                     style='Dark.TButton', state=tk.DISABLED)
        self.stop_button.pack(pady=(10, 0))
        
        # 导入状态
        status_frame = ttk.Frame(step3_frame, style='Dark.TFrame')
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(status_frame, text="导入进度:", style='Dark.TLabel').pack(anchor=tk.W)
        
        self.import_status_text = scrolledtext.ScrolledText(status_frame, 
                                                           height=10,
                                                           bg='#1e1e1e',
                                                           fg='#ffffff',
                                                           insertbackground='#ffffff')
        self.import_status_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 控制变量
        self.import_running = False
        self.import_thread = None
    
    def log(self, message):
        """添加日志信息"""
        try:
            timestamp = time.strftime('%H:%M:%S')
            self.log_text.insert(tk.END, f"{timestamp} - {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            print(f"日志记录失败: {e}")
    
    def log_import(self, message):
        """添加导入日志信息"""
        try:
            timestamp = time.strftime('%H:%M:%S')
            self.import_status_text.insert(tk.END, f"{timestamp} - {message}\n")
            self.import_status_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            print(f"导入日志记录失败: {e}")
    
    def connect_to_premiere(self):
        """连接到Premiere Pro"""
        if not pymiere_available:
            return
        
        def connect():
            try:
                self.log("正在连接 Premiere Pro...")
                
                self.app = pymiere.objects.app
                
                if not self.app:
                    raise Exception("无法获取Premiere Pro应用对象")
                
                self.project = self.app.project
                
                if self.project and hasattr(self.project, 'name'):
                    project_name = self.project.name
                    if project_name:
                        self.connection_label.configure(text=f"已连接: {project_name}")
                        self.log(f"成功连接到项目: {project_name}")
                    else:
                        raise Exception("项目名称为空，可能项目未正确加载")
                else:
                    self.connection_label.configure(text="未找到打开的项目")
                    self.log("错误: 请在Premiere Pro中打开一个项目")
                    
            except Exception as e:
                self.connection_label.configure(text="连接失败")
                error_msg = str(e)
                self.log(f"连接失败: {error_msg}")
        
        threading.Thread(target=connect, daemon=True).start()
    
    def browse_and_match(self):
        """浏览目录并自动匹配"""
        directory = filedialog.askdirectory(title="选择包含SRT文件的目录")
        if directory:
            self.dir_var.set(directory)
            self.srt_directory = directory
            self.log(f"选择目录: {directory}")
            
            # 自动扫描SRT文件
            self.scan_srt_files()
            
            # 自动匹配序列
            if self.srt_files:
                self.match_sequences()
    
    def scan_srt_files(self):
        """扫描SRT文件"""
        if not self.srt_directory:
            messagebox.showwarning("警告", "请先选择SRT文件目录")
            return
        
        try:
            self.srt_files = []
            
            # 扫描目录中的SRT文件
            for file_path in Path(self.srt_directory).rglob("*.srt"):
                self.srt_files.append(str(file_path))
            
            self.log(f"扫描完成，找到 {len(self.srt_files)} 个SRT文件")
            
            if len(self.srt_files) == 0:
                messagebox.showinfo("提示", "在指定目录中未找到SRT文件")
                return False
            else:
                self.log(f"找到 {len(self.srt_files)} 个SRT文件")
                return True
                
        except Exception as e:
            self.log(f"扫描SRT文件时出错: {e}")
            messagebox.showerror("错误", f"扫描失败: {e}")
            return False
    
    def match_sequences(self):
        """智能匹配序列"""
        if not self.project:
            messagebox.showerror("错误", "未连接到Premiere Pro项目")
            return
        
        if not self.srt_files:
            messagebox.showwarning("警告", "请先扫描SRT文件")
            return
        
        try:
            # 清空匹配结果
            for item in self.match_tree.get_children():
                self.match_tree.delete(item)
            
            self.matched_files = []
            
            # 获取项目中的序列
            sequences = self.get_project_sequences()
            self.log(f"找到 {len(sequences)} 个序列")
            
            # 匹配算法
            for srt_file in self.srt_files:
                srt_name = os.path.splitext(os.path.basename(srt_file))[0]
                srt_numbers = self.extract_numbers(srt_name)
                
                best_match = None
                best_match_numbers = []
                
                for sequence in sequences:
                    seq_numbers = self.extract_numbers(sequence['name'])
                    
                    # 检查是否有相同的数字序号
                    common_numbers = [num for num in srt_numbers if num in seq_numbers]
                    if common_numbers:
                        if not best_match or len(common_numbers) > len(best_match_numbers):
                            best_match = sequence
                            best_match_numbers = common_numbers
                
                if best_match:
                    match_info = {
                        'sequence': best_match,
                        'srt_file': srt_file,
                        'srt_name': srt_name,
                        'matched_numbers': best_match_numbers
                    }
                    self.matched_files.append(match_info)
                    
                    # 添加到树形视图
                    self.match_tree.insert('', 'end', values=(
                        best_match['name'],
                        os.path.basename(srt_file),
                        ', '.join(best_match_numbers)
                    ))
                    
                    self.log(f"匹配: {srt_name} -> {best_match['name']} (数字: {', '.join(best_match_numbers)})")
                else:
                    self.log(f"未匹配: {srt_name}")
            
            self.log(f"匹配完成，成功匹配 {len(self.matched_files)} 个文件")
            messagebox.showinfo("匹配完成", f"成功匹配 {len(self.matched_files)} 个SRT文件")
            
        except Exception as e:
            self.log(f"匹配序列时出错: {e}")
            messagebox.showerror("错误", f"匹配失败: {e}")
    
    def get_project_sequences(self):
        """获取项目中的序列"""
        sequences = []
        
        try:
            # 直接获取项目中的所有序列
            if hasattr(self.project, 'sequences'):
                for i in range(len(self.project.sequences)):
                    sequence = self.project.sequences[i]
                    sequences.append({
                        'item': sequence,
                        'name': sequence.name,
                        'path': ""
                    })
                    self.log(f"找到序列: {sequence.name}")
            else:
                # 如果没有sequences属性，尝试从根项目扫描
                root_item = self.project.rootItem
                self.scan_sequences_recursive(root_item, sequences)
        except Exception as e:
            self.log(f"获取序列时出错: {e}")
        
        return sequences
    
    def scan_sequences_recursive(self, item, sequences, path=""):
        """递归扫描序列"""
        try:
            if hasattr(item, 'children') and item.children:
                # 这是一个文件夹
                folder_path = os.path.join(path, item.name) if path else item.name
                for i in range(len(item.children)):
                    self.scan_sequences_recursive(item.children[i], sequences, folder_path)
            else:
                # 检查是否是序列 - 更准确的序列检测
                if hasattr(item, 'type'):
                    # 序列的类型通常是1，但也可能因版本而异
                    if item.type == 1 or (hasattr(item, 'videoTracks') and hasattr(item, 'audioTracks')):
                        sequences.append({
                            'item': item,
                            'name': item.name,
                            'path': path
                        })
                        self.log(f"找到序列: {item.name}")
        except Exception as e:
            self.log(f"扫描序列时出错: {e}")
    
    def extract_numbers(self, filename):
        """提取文件名中的数字序号"""
        numbers = re.findall(r'\d+', filename)
        return numbers
    
    def get_coordinate(self, coord_key):
        """获取坐标"""
        self.log(f"准备获取{coord_key}坐标，请将鼠标移动到目标位置，然后按F1键")
        
        def wait_for_key():
            try:
                # 等待F1键按下
                keyboard.wait('f1')
                
                # 获取当前鼠标位置
                x, y = pyautogui.position()
                self.coordinates[coord_key] = (x, y)
                
                # 更新界面显示
                self.coord_labels[coord_key].configure(text=f"({x}, {y})")
                self.log(f"{coord_key}坐标已设置: ({x}, {y})")
                
                # 自动保存坐标配置
                self.save_coordinates()
                self.update_coordinate_status()
                
            except Exception as e:
                self.log(f"获取坐标时出错: {e}")
        
        # 在新线程中等待按键
        threading.Thread(target=wait_for_key, daemon=True).start()
    
    def test_coordinates(self):
        """测试所有坐标"""
        missing_coords = [key for key, coord in self.coordinates.items() if coord is None]
        
        if missing_coords:
            messagebox.showwarning("警告", f"以下坐标未设置: {', '.join(missing_coords)}")
            return
        
        self.log("开始测试坐标...")
        
        def test():
            try:
                for key, coord in self.coordinates.items():
                    if coord:
                        x, y = coord
                        pyautogui.moveTo(x, y)
                        time.sleep(0.5)
                        self.log(f"测试{key}: ({x}, {y})")
                        
                self.log("坐标测试完成")
                messagebox.showinfo("测试完成", "所有坐标测试完成")
                
            except Exception as e:
                self.log(f"测试坐标时出错: {e}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def start_import_process(self):
        """开始导入流程"""
        if not self.matched_files:
            messagebox.showwarning("警告", "请先完成文件匹配")
            return
        
        missing_coords = [key for key, coord in self.coordinates.items() if coord is None]
        if missing_coords:
            messagebox.showwarning("警告", f"以下坐标未设置: {', '.join(missing_coords)}")
            return
        
        self.import_running = True
        self.execute_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        
        # 清空导入日志
        self.import_status_text.delete(1.0, tk.END)
        
        # 在新线程中执行导入
        self.import_thread = threading.Thread(target=self.import_workflow, daemon=True)
        self.import_thread.start()
        
        # 启动快捷键监听
        self.start_hotkey_listener()
    
    def stop_import_process(self):
        """停止导入流程"""
        self.import_running = False
        self.execute_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.log_import("用户停止了导入流程")
        
        # 停止快捷键监听
        self.stop_hotkey_listener()
    
    def start_hotkey_listener(self):
        """启动快捷键监听"""
        def hotkey_listener():
            try:
                # 监听ESC键
                keyboard.wait('esc')
                if self.import_running:
                    self.log_import("检测到ESC键，正在停止导入...")
                    self.stop_import_process()
            except Exception as e:
                self.log_import(f"快捷键监听出错: {e}")
        
        # 在新线程中启动监听
        self.hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
        self.hotkey_thread.start()
        self.log_import("快捷键监听已启动 - 按ESC键可停止导入")
    
    def stop_hotkey_listener(self):
        """停止快捷键监听"""
        try:
            # keyboard库的监听会在线程结束时自动停止
            pass
        except Exception as e:
            self.log_import(f"停止快捷键监听出错: {e}")
    
    def import_workflow(self):
        """导入工作流程"""
        try:
            self.log_import("开始SRT字幕自动导入流程")
            
            # 按数字顺序排序文件
            sorted_files = sorted(self.matched_files, 
                                key=lambda x: [int(n) for n in self.extract_numbers(x['srt_name']) if n.isdigit()])
            
            total_files = len(sorted_files)
            is_first_file = True
            
            for i, match_info in enumerate(sorted_files):
                if not self.import_running:
                    self.log_import("导入已停止")
                    break
                
                srt_file = match_info['srt_file']
                sequence = match_info['sequence']
                
                self.log_import(f"导入文件 {i+1}/{total_files}: {os.path.basename(srt_file)}")
                
                # 更新进度
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                
                # 再次检查停止标志
                if not self.import_running:
                    self.log_import("导入已停止")
                    break
                
                # 设置当前序列为活动序列
                try:
                    self.project.activeSequence = sequence['item']
                    self.log_import(f"  切换到序列: {sequence['name']}")
                    # 切换序列后等待界面稳定
                    time.sleep(0.5)  # 进一步减少序列切换等待时间
                except Exception as e:
                    self.log_import(f"  切换序列失败: {e}")
                
                # 再次检查停止标志
                if not self.import_running:
                    self.log_import("导入已停止")
                    break
                
                # 执行导入步骤
                success = self.import_single_file(srt_file, is_first_file)
                
                if success:
                    self.log_import(f"  导入成功")
                    is_first_file = False  # 第一个文件后，后续不需要粘贴路径
                else:
                    self.log_import(f"  导入失败")
                
                # 短暂停顿，同时检查停止标志
                for _ in range(10):  # 分成10个0.1秒的检查
                    if not self.import_running:
                        self.log_import("导入已停止")
                        break
                    time.sleep(0.1)
            

            
            self.progress_var.set(100)
            self.log_import("SRT字幕导入流程完成!")
            
            if self.import_running:
                messagebox.showinfo("完成", f"成功导入 {total_files} 个SRT字幕文件!")
            
        except Exception as e:
            self.log_import(f"导入流程出错: {e}")
            traceback.print_exc()
        
        finally:
            self.import_running = False
            self.execute_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
    
    def import_single_file(self, srt_file, is_first_file):
        """导入单个SRT文件"""
        try:
            # 步骤1: 点击文件导入按钮
            x, y = self.coordinates['import_button']
            self.log_import(f"  点击导入按钮坐标: ({x}, {y})")
            
            # 确保鼠标移动到正确位置并点击
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click(x, y)
            time.sleep(1.2)  # 等待导入对话框打开
            
            if is_first_file:
                # 只有第一个文件需要导航到目录
                # 使用剪贴板粘贴目录路径，避免特殊字符问题
                import pyperclip
                pyperclip.copy(self.srt_directory)
                
                # 在地址栏粘贴目录路径
                pyautogui.hotkey('ctrl', 'l')  # 聚焦地址栏
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'v')  # 粘贴路径
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.8)
                
                # 按Alt+N（如果需要）
                pyautogui.hotkey('alt', 'n')
                time.sleep(0.3)
            
            # 使用剪贴板粘贴文件名并确认
            filename = os.path.basename(srt_file)
            import pyperclip
            pyperclip.copy(filename)
            pyautogui.hotkey('ctrl', 'v')  # 粘贴文件名
            time.sleep(0.3)
            pyautogui.press('enter')  # 确认选择文件
            time.sleep(1.0)  # 等待文件选择完成
            
            # 步骤2: 点击字幕样式下拉菜单
            x, y = self.coordinates['style_dropdown']
            self.log_import(f"  步骤2: 点击样式下拉菜单坐标: ({x}, {y})")
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click(x, y)
            self.log_import(f"  步骤2: 已点击下拉菜单，等待菜单展开...")
            time.sleep(0.5)  # 进一步减少等待时间
            
            # 步骤3: 选择字幕样式
            x, y = self.coordinates['style_select']
            self.log_import(f"  步骤3: 点击样式选择坐标: ({x}, {y})")
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click(x, y)
            self.log_import(f"  步骤3: 已点击样式选择，等待选择完成...")
            time.sleep(0.5)  # 进一步减少等待时间
            
            # 步骤4: 点击确定按钮
            x, y = self.coordinates['confirm_button']
            self.log_import(f"  步骤4: 点击确定按钮坐标: ({x}, {y})")
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click(x, y)
            self.log_import(f"  步骤4: 已点击确定按钮，等待导入完成...")
            time.sleep(0.6)  # 进一步减少等待时间
            
            return True
            
        except Exception as e:
            self.log_import(f"  导入单个文件时出错: {e}")
            return False
    
    def load_coordinates(self):
        """加载保存的坐标配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_coords = json.load(f)
                
                # 更新坐标配置
                for key, value in saved_coords.items():
                    if key in self.coordinates and value is not None:
                        self.coordinates[key] = tuple(value)
                
                self.log(f"已加载保存的坐标配置: {len([v for v in saved_coords.values() if v is not None])} 个坐标")
            else:
                self.log("未找到保存的坐标配置文件")
        except Exception as e:
            self.log(f"加载坐标配置失败: {e}")
    
    def save_coordinates(self):
        """保存坐标配置到文件"""
        try:
            # 准备保存的数据
            save_data = {}
            for key, value in self.coordinates.items():
                save_data[key] = list(value) if value is not None else None
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.log("坐标配置已自动保存")
        except Exception as e:
            self.log(f"保存坐标配置失败: {e}")
    
    def update_coordinate_display(self):
        """更新坐标显示"""
        if hasattr(self, 'coord_labels'):
            for key, coord in self.coordinates.items():
                if key in self.coord_labels:
                    if coord is not None:
                        self.coord_labels[key].configure(text=f"({coord[0]}, {coord[1]})")
                    else:
                        self.coord_labels[key].configure(text="未设置")
        
        # 更新状态提示
        if hasattr(self, 'coord_status_label'):
            self.update_coordinate_status()
    
    def update_coordinate_status(self):
        """更新坐标配置状态提示"""
        try:
            set_count = len([v for v in self.coordinates.values() if v is not None])
            total_count = len(self.coordinates)
            
            if set_count == 0:
                status_text = "尚未配置任何坐标"
                color = "#ff6b6b"  # 红色
            elif set_count == total_count:
                status_text = f"✓ 所有坐标已配置完成 ({set_count}/{total_count}) - 已自动保存"
                color = "#51cf66"  # 绿色
            else:
                status_text = f"已配置 {set_count}/{total_count} 个坐标 - 已自动保存"
                color = "#ffd43b"  # 黄色
            
            if hasattr(self, 'coord_status_label') and self.coord_status_label:
                self.coord_status_label.configure(text=status_text, foreground=color)
        except Exception as e:
            self.log(f"更新坐标状态失败: {e}")
    
    def clear_coordinates(self):
        """清除所有坐标配置"""
        try:
            result = messagebox.askyesno("确认清除", "确定要清除所有已配置的坐标吗？")
            if result:
                # 清除内存中的坐标
                for key in self.coordinates:
                    self.coordinates[key] = None
                
                # 更新界面显示
                self.update_coordinate_display()
                
                # 删除配置文件
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                
                self.log("所有坐标配置已清除")
                messagebox.showinfo("清除完成", "所有坐标配置已清除")
        except Exception as e:
            self.log(f"清除坐标配置失败: {e}")
            messagebox.showerror("清除失败", f"清除坐标配置失败: {e}")

def main():
    """主函数"""
    try:
        # 检查必要的库
        try:
            import pyautogui
            import keyboard
        except ImportError as e:
            print(f"缺少必要的库: {e}")
            print("请运行: pip install pyautogui keyboard")
            input("按回车键退出...")
            return
        
        root = tk.Tk()
        app = SRTSubtitleImporter(root)
        
        # 设置窗口图标（如果有的话）
        try:
            root.iconbitmap('../icons/smart_editing.ico')
        except:
            pass
        
        # 启动应用
        root.mainloop()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()