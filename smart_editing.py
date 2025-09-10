"""
Smart Editing - Premiere Pro 智能序列创建工具
自动化音视频匹配和序列创建，提升剪辑效率
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import re
import threading
from pathlib import Path
from collections import defaultdict
import time
import sys
import traceback

# 尝试导入pymiere，如果失败则提供错误信息
try:
    import pymiere
    PYMIERE_AVAILABLE = True
    PYMIERE_ERROR = None
except ImportError as e:
    PYMIERE_AVAILABLE = False
    PYMIERE_ERROR = str(e)
except Exception as e:
    PYMIERE_AVAILABLE = False
    PYMIERE_ERROR = str(e)

class SmartEditingApp:
    def __init__(self, root):
        self.root = root
        self.app = None
        self.project = None
        self.setup_ui()
        
        # 延迟连接，避免启动时卡顿
        self.root.after(1000, self.connect_to_premiere)
    
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("Smart Editing - Premiere Pro 智能序列创建工具")
        self.root.geometry("600x500")
        self.root.configure(bg='#2b2b2b')  # 深色主题
        
        # 设置样式
        try:
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Dark.TFrame', background='#2b2b2b')
            style.configure('Dark.TLabel', background='#2b2b2b', foreground='#ffffff')
            style.configure('Dark.TButton', background='#404040', foreground='#ffffff')
            style.map('Dark.TButton', background=[('active', '#505050')])
            
            # 配置复选框样式，使其显示对勾
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
        
        title_label = ttk.Label(title_frame, text="Smart Editing", 
                               font=('Arial', 18, 'bold'), style='Dark.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="智能序列创建工具 v1.0", 
                                  font=('Arial', 10), style='Dark.TLabel')
        subtitle_label.pack()
        
        # 连接状态
        self.status_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        if not PYMIERE_AVAILABLE:
            self.connection_label = ttk.Label(self.status_frame, 
                                             text="错误: pymiere库未安装", 
                                             style='Dark.TLabel')
        else:
            self.connection_label = ttk.Label(self.status_frame, 
                                             text="正在连接 Premiere Pro...", 
                                             style='Dark.TLabel')
        self.connection_label.pack()
        
        # 功能选项区域
        options_frame = ttk.LabelFrame(main_frame, text="功能选项", style='Dark.TFrame')
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 静音视频选项
        self.mute_video_var = tk.BooleanVar(value=False)
        self.mute_checkbox = ttk.Checkbutton(options_frame, 
                                           text="静音视频轨道 (推荐：使用外录音频时勾选)",
                                           variable=self.mute_video_var,
                                           style='Dark.TCheckbutton')
        self.mute_checkbox.pack(anchor=tk.W, padx=10, pady=10)
        
        # 主功能按钮区域
        button_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 一键创建序列按钮
        self.create_button = ttk.Button(button_frame, 
                                       text="一键创建序列",
                                       command=self.start_sequence_creation,
                                       style='Dark.TButton')
        self.create_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新项目按钮
        self.refresh_button = ttk.Button(button_frame,
                                        text="刷新项目", 
                                        command=self.refresh_project,
                                        style='Dark.TButton')
        self.refresh_button.pack(side=tk.LEFT)
        
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
                                                 height=15,
                                                 bg='#1e1e1e',
                                                 fg='#ffffff',
                                                 insertbackground='#ffffff')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始化按钮状态
        self.create_button.configure(state=tk.DISABLED)
        self.refresh_button.configure(state=tk.DISABLED)
        
        # 如果pymiere不可用，显示错误信息
        if not PYMIERE_AVAILABLE:
            self.log(f"错误: pymiere库未安装 - {PYMIERE_ERROR}")
            self.log("请运行: pip install pymiere")
    
    def log(self, message):
        """添加日志信息"""
        try:
            timestamp = time.strftime('%H:%M:%S')
            self.log_text.insert(tk.END, f"{timestamp} - {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            print(f"日志记录失败: {e}")
    
    def connect_to_premiere(self):
        """连接到Premiere Pro"""
        if not PYMIERE_AVAILABLE:
            return
        
        def connect():
            try:
                self.app = pymiere.objects.app
                self.project = self.app.project
                
                if self.project:
                    project_name = self.project.name
                    self.connection_label.configure(text=f"已连接: {project_name}")
                    self.create_button.configure(state=tk.NORMAL)
                    self.refresh_button.configure(state=tk.NORMAL)
                    self.log(f"成功连接到项目: {project_name}")
                else:
                    self.connection_label.configure(text="未找到打开的项目")
                    self.log("错误: 请在Premiere Pro中打开一个项目")
                    
            except Exception as e:
                self.connection_label.configure(text="连接失败")
                self.log(f"连接失败: {e}")
                self.log("请确保Premiere Pro已启动并打开项目")
        
        # 在新线程中连接，避免界面卡顿
        threading.Thread(target=connect, daemon=True).start()
    
    def refresh_project(self):
        """刷新项目连接"""
        self.connection_label.configure(text="正在刷新...")
        self.create_button.configure(state=tk.DISABLED)
        self.refresh_button.configure(state=tk.DISABLED)
        self.connect_to_premiere()
    
    def start_sequence_creation(self):
        """开始序列创建流程"""
        if not PYMIERE_AVAILABLE:
            messagebox.showerror("错误", "pymiere库未安装，无法使用")
            return
            
        if not self.project:
            messagebox.showerror("错误", "未连接到Premiere Pro项目")
            return
        
        # 禁用按钮防止重复操作
        self.create_button.configure(state=tk.DISABLED)
        self.refresh_button.configure(state=tk.DISABLED)
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        # 在新线程中执行，避免界面卡顿
        threading.Thread(target=self.create_sequences_workflow, daemon=True).start()
    
    def create_sequences_workflow(self):
        """序列创建工作流程"""
        try:
            self.log("开始智能序列创建流程")
            
            # 步骤1: 扫描项目文件
            self.log("步骤1: 扫描项目文件...")
            self.progress_var.set(10)
            
            video_files, audio_files = self.scan_project_files()
            
            if not video_files:
                self.log("项目中未找到视频文件")
                messagebox.showwarning("提示", "项目中未找到视频文件")
                return
            
            self.log(f"找到 {len(video_files)} 个视频文件")
            self.log(f"找到 {len(audio_files)} 个音频文件")
            
            # 步骤2: 智能音视频匹配
            self.log("步骤2: 智能音视频匹配...")
            self.progress_var.set(30)
            
            matches = self.match_audio_video(video_files, audio_files)
            self.log(f"完成匹配，共 {len(matches)} 组")
            
            # 步骤3: 创建序列
            self.log("步骤3: 创建序列...")
            self.progress_var.set(50)
            
            sequences_created = self.create_sequences_from_matches(matches)
            
            # 步骤4: 归档序列
            self.log("步骤4: 序列归档管理...")
            self.progress_var.set(80)
            
            self.organize_sequences(sequences_created)
            
            # 完成
            self.progress_var.set(100)
            self.log("序列创建流程完成!")
            self.log(f"统计: 成功创建 {len(sequences_created)} 个序列")
            
            messagebox.showinfo("完成", f"成功创建 {len(sequences_created)} 个序列!")
            
        except Exception as e:
            error_msg = f"操作失败: {e}"
            self.log(f"错误: {error_msg}")
            traceback.print_exc()
            messagebox.showerror("错误", error_msg)
        
        finally:
            # 恢复按钮状态
            self.create_button.configure(state=tk.NORMAL)
            self.refresh_button.configure(state=tk.NORMAL)
    
    def scan_project_files(self):
        """扫描项目文件"""
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv'}
        audio_extensions = {'.mp3', '.wav', '.aac', '.m4a'}
        
        video_files = []
        audio_files = []
        
        def scan_item(item, path=""):
            """递归扫描项目项目"""
            try:
                if hasattr(item, 'children') and item.children:
                    # 这是一个文件夹
                    folder_path = os.path.join(path, item.name) if path else item.name
                    for i in range(len(item.children)):
                        scan_item(item.children[i], folder_path)
                else:
                    # 这是一个文件
                    file_name = item.name
                    file_ext = os.path.splitext(file_name)[1].lower()
                    
                    if file_ext in video_extensions:
                        video_files.append({
                            'item': item,
                            'name': file_name,
                            'path': path,
                            'full_path': os.path.join(path, file_name) if path else file_name
                        })
                        self.log(f"  视频: {file_name}")
                    
                    elif file_ext in audio_extensions:
                        audio_files.append({
                            'item': item,
                            'name': file_name,
                            'path': path,
                            'full_path': os.path.join(path, file_name) if path else file_name
                        })
                        self.log(f"  音频: {file_name}")
                        
            except Exception as e:
                self.log(f"扫描项目时出错: {e}")
        
        # 开始扫描
        try:
            root_item = self.project.rootItem
            if hasattr(root_item, 'children'):
                for i in range(len(root_item.children)):
                    scan_item(root_item.children[i])
        except Exception as e:
            self.log(f"扫描项目根目录失败: {e}")
        
        return video_files, audio_files
    
    def match_audio_video(self, video_files, audio_files):
        """智能音视频匹配"""
        matches = []
        
        def extract_numbers(filename):
            """提取文件名中的数字序号"""
            # 移除扩展名
            name_without_ext = os.path.splitext(filename)[0]
            # 提取所有数字
            numbers = re.findall(r'\d+', name_without_ext)
            return numbers
        
        for video in video_files:
            video_numbers = extract_numbers(video['name'])
            matched_audios = []
            
            self.log(f"匹配视频: {video['name']} (数字: {video_numbers})")
            
            # 为每个视频查找匹配的音频
            for audio in audio_files:
                audio_numbers = extract_numbers(audio['name'])
                
                # 检查是否有相同的数字序号
                if any(num in audio_numbers for num in video_numbers):
                    matched_audios.append(audio)
                    self.log(f"  匹配音频: {audio['name']} (数字: {audio_numbers})")
            
            # 创建匹配记录
            match = {
                'video': video,
                'audios': matched_audios,
                'sequence_name': os.path.splitext(video['name'])[0]
            }
            matches.append(match)
            
            if not matched_audios:
                self.log(f"  无匹配音频")
            else:
                self.log(f"  匹配到 {len(matched_audios)} 个音频文件")
        
        return matches
    
    def create_sequences_from_matches(self, matches):
        """根据匹配结果创建序列 - 使用"从剪辑新建序列"功能"""
        sequences_created = []
        total_matches = len(matches)
        
        for i, match in enumerate(matches):
            try:
                video = match['video']
                audios = match['audios']
                sequence_name = match['sequence_name']
                
                self.log(f"创建序列: {sequence_name}")
                
                # 更新进度
                progress = 50 + (i / total_matches) * 25  # 50-75%
                self.progress_var.set(progress)
                
                # 使用"从剪辑新建序列"功能
                new_sequence = self.create_sequence_from_clip(video, sequence_name)
                
                if new_sequence:
                    self.log(f"  序列创建成功")
                    
                    # 设置为活动序列
                    self.project.activeSequence = new_sequence
                    
                    # 添加音频到序列
                    if audios:
                        self.add_audios_to_sequence(new_sequence, audios)
                    
                    # 处理视频轨道静音
                    if self.mute_video_var.get():
                        self.mute_video_track(new_sequence)
                    
                    sequences_created.append(new_sequence)
                    self.log(f"  序列配置完成")
                    
                else:
                    self.log(f"  序列创建失败")
                    
            except Exception as e:
                self.log(f"  创建序列时出错: {e}")
                import traceback
                traceback.print_exc()
        
        return sequences_created
    
    def create_sequence_from_clip(self, video, sequence_name):
        """从剪辑创建序列 - 使用createNewSequenceFromClips方法"""
        try:
            self.log(f"    使用'从剪辑新建序列'功能...")
            
            new_sequence = self.project.createNewSequenceFromClips(
                sequence_name, 
                [video['item']], 
                self.project.rootItem
            )
            
            if new_sequence:
                self.log(f"    成功创建序列，视频已自动添加")
                return new_sequence
            else:
                self.log(f"    createNewSequenceFromClips返回None")
                return None
            
        except Exception as e:
            self.log(f"    从剪辑创建序列失败: {e}")
            return None
    

    
    def add_video_to_sequence(self, sequence, video):
        """添加视频到序列"""
        try:
            video_tracks = sequence.videoTracks
            if len(video_tracks) > 0:
                video_track = video_tracks[0]
                
                # 尝试不同的时间格式
                time_formats = [0, "00:00:00:00"]
                
                for time_format in time_formats:
                    try:
                        result = video_track.insertClip(video['item'], time_format)
                        if result:
                            self.log(f"    视频已添加到轨道（时间格式: {time_format}）")
                            return True
                    except Exception as e:
                        self.log(f"    时间格式 {time_format} 失败: {e}")
                        continue
                
                # 如果插入失败，尝试覆盖
                try:
                    result = video_track.overwriteClip(video['item'], 0)
                    if result:
                        self.log(f"    视频已覆盖到轨道")
                        return True
                except Exception as e:
                    self.log(f"    覆盖方法也失败: {e}")
                
                self.log(f"    所有视频添加方法均失败")
                return False
            else:
                self.log(f"    没有可用的视频轨道")
                return False
                
        except Exception as e:
            self.log(f"    添加视频时出错: {e}")
            return False
    
    def add_audios_to_sequence(self, sequence, audios):
        """添加音频到序列（多轨道智能布局）"""
        try:
            # 按文件夹分组音频
            folder_groups = defaultdict(list)
            for audio in audios:
                folder_path = audio['path'] if audio['path'] else "根目录"
                folder_groups[folder_path].append(audio)
            
            audio_tracks = sequence.audioTracks
            
            # 检测视频占用的音频轨道数量
            video_audio_tracks_used = self.detect_video_audio_tracks(sequence)
            self.log(f"    视频音频占用了前 {video_audio_tracks_used} 个轨道")
            
            # 从视频音频轨道之后开始分配外录音频
            track_index = video_audio_tracks_used
            
            for folder_path, folder_audios in folder_groups.items():
                self.log(f"    处理文件夹: {folder_path}")
                
                # 确保有足够的音频轨道
                if track_index >= len(audio_tracks):
                    self.log(f"    音频轨道不足，跳过部分音频")
                    break
                
                audio_track = audio_tracks[track_index]
                self.log(f"    使用音频轨道 {track_index + 1} ({audio_track.name})")
                
                # 添加该文件夹的所有音频到同一轨道
                for audio in folder_audios:
                    try:
                        result = audio_track.insertClip(audio['item'], 0)
                        if result:
                            self.log(f"      音频已添加: {audio['name']}")
                        else:
                            self.log(f"      音频添加失败: {audio['name']}")
                    except Exception as e:
                        self.log(f"      添加音频时出错: {e}")
                
                track_index += 1
                
        except Exception as e:
            self.log(f"    音频处理出错: {e}")
    
    def detect_video_audio_tracks(self, sequence):
        """检测视频音频占用的轨道数量"""
        try:
            audio_tracks = sequence.audioTracks
            used_tracks = 0
            
            # 检查前几个音频轨道是否有来自视频的音频
            for i in range(min(3, len(audio_tracks))):  # 最多检查前3个轨道
                track = audio_tracks[i]
                clips = track.clips
                
                if len(clips) > 0:
                    # 检查第一个片段是否来自视频文件
                    first_clip = clips[0]
                    clip_name = first_clip.name
                    
                    # 如果片段名称是视频文件名（没有音频文件扩展名），则认为是视频音频
                    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv']
                    audio_extensions = ['.mp3', '.wav', '.aac', '.m4a']
                    
                    clip_ext = os.path.splitext(clip_name)[1].lower()
                    
                    if clip_ext in video_extensions:
                        used_tracks = i + 1
                        self.log(f"      轨道 {i + 1} 有视频音频: {clip_name}")
                    else:
                        # 如果遇到非视频音频，停止检查
                        break
                else:
                    # 如果轨道为空，停止检查
                    break
            
            # 如果没有检测到视频音频，默认视频占用1个轨道（A1）
            if used_tracks == 0:
                used_tracks = 1
                self.log(f"      默认视频占用A1轨道")
            
            return used_tracks
            
        except Exception as e:
            self.log(f"    检测视频音频轨道失败: {e}")
            # 出错时默认视频占用1个轨道
            return 1
    
    def mute_video_track(self, sequence):
        """静音视频轨道的音频"""
        try:
            audio_tracks = sequence.audioTracks
            
            # 检测视频占用的音频轨道数量
            video_audio_tracks_used = self.detect_video_audio_tracks(sequence)
            
            # 静音所有被视频占用的音频轨道
            muted_count = 0
            for i in range(min(video_audio_tracks_used, len(audio_tracks))):
                audio_track = audio_tracks[i]
                try:
                    result = audio_track.setMute(1)  # 1 = 静音
                    
                    if audio_track.isMuted():
                        muted_count += 1
                        self.log(f"    轨道 {i + 1} ({audio_track.name}) 已静音")
                    else:
                        self.log(f"    轨道 {i + 1} ({audio_track.name}) 静音失败")
                except Exception as e:
                    self.log(f"    静音轨道 {i + 1} 时出错: {e}")
            
            if muted_count > 0:
                self.log(f"    成功静音 {muted_count} 个视频音频轨道")
            else:
                self.log(f"    没有成功静音任何轨道")
                
        except Exception as e:
            self.log(f"    静音视频轨道时出错: {e}")
    
    def organize_sequences(self, sequences):
        """序列归档管理"""
        try:
            # 查找或创建"序列"文件夹
            root_item = self.project.rootItem
            sequence_folder = None
            
            # 查找现有的序列文件夹
            if hasattr(root_item, 'children'):
                for i in range(len(root_item.children)):
                    item = root_item.children[i]
                    if hasattr(item, 'children') and item.name == "序列":
                        sequence_folder = item
                        self.log("找到现有序列文件夹")
                        break
            
            # 如果没有找到，创建新的序列文件夹
            if not sequence_folder:
                self.log("尝试创建序列文件夹...")
                self.log("注意：pymiere可能不支持直接创建文件夹")
                self.log("建议手动在项目面板中创建'序列'文件夹")
            
            # 移动序列到文件夹（这个功能在pymiere中可能有限制）
            if sequence_folder:
                self.log(f"序列归档功能需要手动操作")
                self.log(f"请手动将创建的序列拖拽到'序列'文件夹中")
            else:
                self.log(f"序列已创建在项目根目录")
                
        except Exception as e:
            self.log(f"序列归档时出错: {e}")

def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = SmartEditingApp(root)
        
        # 设置窗口图标（如果有的话）
        try:
            root.iconbitmap('icon.ico')
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