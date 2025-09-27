"""
SRT字幕自动导入工具 - 测试版本
简化版本用于测试基本功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re
from pathlib import Path

class SRTImporterTest:
    def __init__(self, root):
        self.root = root
        self.srt_directory = ""
        self.srt_files = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("SRT字幕导入工具 - 测试版")
        self.root.geometry("600x400")
        self.root.configure(bg='#2b2b2b')
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background='#2b2b2b')
        style.configure('Dark.TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('Dark.TButton', background='#404040', foreground='#ffffff')
        style.map('Dark.TButton', background=[('active', '#505050')])
        
        # 主框架
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="SRT字幕导入工具 - 测试版", 
                               font=('Arial', 16, 'bold'), style='Dark.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 目录选择
        dir_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        dir_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(dir_frame, text="SRT文件目录:", style='Dark.TLabel').pack(anchor=tk.W)
        
        dir_select_frame = ttk.Frame(dir_frame, style='Dark.TFrame')
        dir_select_frame.pack(fill=tk.X, pady=5)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_select_frame, textvariable=self.dir_var, width=50)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(dir_select_frame, text="浏览", 
                                  command=self.browse_directory, style='Dark.TButton')
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 扫描按钮
        scan_button = ttk.Button(dir_frame, text="扫描SRT文件", 
                                command=self.scan_srt_files, style='Dark.TButton')
        scan_button.pack(pady=10)
        
        # 文件列表
        ttk.Label(dir_frame, text="找到的SRT文件:", style='Dark.TLabel').pack(anchor=tk.W)
        
        self.file_listbox = tk.Listbox(dir_frame, height=10, bg='#1e1e1e', fg='#ffffff')
        self.file_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 测试按钮
        test_button = ttk.Button(main_frame, text="测试文件匹配算法", 
                                command=self.test_matching, style='Dark.TButton')
        test_button.pack(pady=10)
        
        # 结果显示
        self.result_text = tk.Text(main_frame, height=8, bg='#1e1e1e', fg='#ffffff')
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(title="选择包含SRT文件的目录")
        if directory:
            self.dir_var.set(directory)
            self.srt_directory = directory
            self.log(f"选择目录: {directory}")
    
    def scan_srt_files(self):
        """扫描SRT文件"""
        if not self.srt_directory:
            messagebox.showwarning("警告", "请先选择SRT文件目录")
            return
        
        try:
            self.srt_files = []
            self.file_listbox.delete(0, tk.END)
            
            # 扫描目录中的SRT文件
            for file_path in Path(self.srt_directory).rglob("*.srt"):
                self.srt_files.append(str(file_path))
                self.file_listbox.insert(tk.END, file_path.name)
            
            self.log(f"扫描完成，找到 {len(self.srt_files)} 个SRT文件")
            
            if len(self.srt_files) == 0:
                messagebox.showinfo("提示", "在指定目录中未找到SRT文件")
            else:
                messagebox.showinfo("扫描完成", f"找到 {len(self.srt_files)} 个SRT文件")
                
        except Exception as e:
            self.log(f"扫描SRT文件时出错: {e}")
            messagebox.showerror("错误", f"扫描失败: {e}")
    
    def test_matching(self):
        """测试匹配算法"""
        if not self.srt_files:
            messagebox.showwarning("警告", "请先扫描SRT文件")
            return
        
        self.result_text.delete(1.0, tk.END)
        self.log("开始测试文件匹配算法...")
        
        # 模拟一些序列名称进行测试（这些应该是PR中已创建的序列）
        test_sequences = [
            "序列01", "序列02", "序列03", "序列04", "序列05",
            "Sequence_01", "Sequence_02", "Sequence_03",
            "字幕序列-10", "字幕序列-11", "字幕序列-12",
            "Episode01", "Episode02", "Episode03"
        ]
        
        self.log("模拟序列:")
        for seq in test_sequences:
            self.log(f"  {seq}")
        
        self.log("\n匹配结果:")
        
        for srt_file in self.srt_files:
            srt_name = os.path.splitext(os.path.basename(srt_file))[0]
            srt_numbers = self.extract_numbers(srt_name)
            
            best_match = None
            best_match_numbers = []
            
            for sequence in test_sequences:
                seq_numbers = self.extract_numbers(sequence)
                
                # 检查是否有相同的数字序号
                common_numbers = [num for num in srt_numbers if num in seq_numbers]
                if common_numbers:
                    if not best_match or len(common_numbers) > len(best_match_numbers):
                        best_match = sequence
                        best_match_numbers = common_numbers
            
            if best_match:
                self.log(f"✓ {srt_name} -> {best_match} (匹配数字: {', '.join(best_match_numbers)})")
            else:
                self.log(f"✗ {srt_name} -> 无匹配")
        
        self.log("\n测试完成!")
    
    def extract_numbers(self, filename):
        """提取文件名中的数字序号"""
        numbers = re.findall(r'\d+', filename)
        return numbers
    
    def log(self, message):
        """添加日志信息"""
        self.result_text.insert(tk.END, f"{message}\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()

def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = SRTImporterTest(root)
        root.mainloop()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()