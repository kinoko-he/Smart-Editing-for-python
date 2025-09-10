import pymiere

class AudioMuteController:
    def __init__(self):
        self.app = None
        self.project = None
        self.sequence = None
    
    def connect(self):
        """连接到Premiere Pro"""
        try:
            self.app = pymiere.objects.app
            self.project = self.app.project
            if self.project:
                print(f"[连接成功] {self.project.name}")
                return True
        except Exception as e:
            print(f"[连接失败] {e}")
            return False
    
    def set_sequence(self, sequence_name):
        """设置目标序列"""
        try:
            for seq in self.project.sequences:
                if seq.name == sequence_name:
                    self.sequence = seq
                    self.project.activeSequence = seq
                    print(f"[设置序列] {sequence_name}")
                    return True
            print(f"[错误] 未找到序列: {sequence_name}")
            return False
        except Exception as e:
            print(f"[错误] 设置序列失败: {e}")
            return False
    
    def list_audio_tracks(self):
        """列出所有音频轨道及其状态"""
        if not self.sequence:
            print("[错误] 请先设置序列")
            return []
        
        try:
            audio_tracks = self.sequence.audioTracks
            print(f"\n=== 音频轨道列表 ===")
            
            track_info = []
            for i, track in enumerate(audio_tracks, 1):
                is_muted = track.isMuted()
                clips_count = len(track.clips)
                
                info = {
                    'index': i,
                    'name': track.name,
                    'muted': is_muted,
                    'clips': clips_count,
                    'track_obj': track
                }
                
                track_info.append(info)
                
                status = "[静音]" if is_muted else "[正常]"
                print(f"{i}. {track.name} {status} - {clips_count}个片段")
            
            return track_info
            
        except Exception as e:
            print(f"[错误] 获取音频轨道失败: {e}")
            return []
    
    def mute_track(self, track_index, mute=True):
        """静音或取消静音指定轨道 (使用整数参数)"""
        try:
            audio_tracks = self.sequence.audioTracks
            
            if track_index < 1 or track_index > len(audio_tracks):
                print(f"[错误] 轨道索引超出范围: {track_index}")
                return False
            
            track = audio_tracks[track_index - 1]
            
            # 获取当前状态
            current_muted = track.isMuted()
            print(f"[操作前] {track.name} 静音状态: {current_muted}")
            
            # 使用整数参数: 1=静音, 0=取消静音
            mute_value = 1 if mute else 0
            result = track.setMute(mute_value)
            
            # 验证结果
            new_muted = track.isMuted()
            print(f"[操作后] {track.name} 静音状态: {new_muted}")
            
            if new_muted == mute:
                action = "静音" if mute else "取消静音"
                print(f"[成功] 轨道 {track_index} ({track.name}) {action}成功!")
                return True
            else:
                print(f"[失败] 静音状态未能正确设置")
                return False
                
        except Exception as e:
            print(f"[错误] 静音操作失败: {e}")
            return False
    
    def mute_multiple_tracks(self, track_indices, mute=True):
        """批量静音多个轨道"""
        results = []
        action = "静音" if mute else "取消静音"
        
        print(f"\n[批量{action}] 轨道: {track_indices}")
        
        for track_index in track_indices:
            success = self.mute_track(track_index, mute)
            results.append((track_index, success))
        
        successful = sum(1 for _, success in results if success)
        print(f"\n[批量结果] {successful}/{len(track_indices)} 个轨道{action}成功")
        
        return results
    
    def toggle_track_mute(self, track_index):
        """切换轨道的静音状态"""
        try:
            audio_tracks = self.sequence.audioTracks
            
            if track_index < 1 or track_index > len(audio_tracks):
                print(f"[错误] 轨道索引超出范围: {track_index}")
                return False
            
            track = audio_tracks[track_index - 1]
            current_muted = track.isMuted()
            
            # 切换状态
            new_mute_state = not current_muted
            return self.mute_track(track_index, new_mute_state)
            
        except Exception as e:
            print(f"[错误] 切换静音状态失败: {e}")
            return False
    
    def mute_all_tracks(self):
        """静音所有音频轨道"""
        if not self.sequence:
            return False
        
        audio_tracks = self.sequence.audioTracks
        all_indices = list(range(1, len(audio_tracks) + 1))
        
        return self.mute_multiple_tracks(all_indices, True)
    
    def unmute_all_tracks(self):
        """取消静音所有音频轨道"""
        if not self.sequence:
            return False
        
        audio_tracks = self.sequence.audioTracks
        all_indices = list(range(1, len(audio_tracks) + 1))
        
        return self.mute_multiple_tracks(all_indices, False)
    
    def get_muted_tracks(self):
        """获取所有静音的轨道"""
        track_info = self.list_audio_tracks()
        muted_tracks = [info for info in track_info if info['muted']]
        
        if muted_tracks:
            print(f"\n[静音轨道] {len(muted_tracks)} 个轨道处于静音状态:")
            for info in muted_tracks:
                print(f"   {info['index']}. {info['name']}")
        else:
            print(f"\n[静音轨道] 没有轨道处于静音状态")
        
        return muted_tracks

def demo_working_audio_mute():
    """演示工作的音频静音功能"""
    
    print("=== Pymiere 音频轨道静音功能演示 ===")
    
    controller = AudioMuteController()
    
    if not controller.connect():
        return
    
    if not controller.set_sequence("001"):
        return
    
    # 显示初始状态
    print("\n1. 初始状态:")
    track_info = controller.list_audio_tracks()
    
    if not track_info:
        print("没有音频轨道可供测试")
        return
    
    # 测试静音第1个轨道
    print(f"\n2. 静音第1个轨道:")
    success = controller.mute_track(1, True)
    if success:
        controller.list_audio_tracks()
    
    # 测试取消静音
    print(f"\n3. 取消静音第1个轨道:")
    success = controller.mute_track(1, False)
    if success:
        controller.list_audio_tracks()
    
    # 测试批量静音前2个轨道
    if len(track_info) >= 2:
        print(f"\n4. 批量静音前2个轨道:")
        controller.mute_multiple_tracks([1, 2], True)
        controller.list_audio_tracks()
        
        # 显示静音轨道
        controller.get_muted_tracks()
        
        # 恢复
        print(f"\n5. 恢复所有轨道:")
        controller.unmute_all_tracks()
        controller.list_audio_tracks()
    
    # 测试切换功能
    print(f"\n6. 测试切换第1个轨道静音状态:")
    controller.toggle_track_mute(1)
    controller.list_audio_tracks()
    
    # 再次切换回来
    print(f"\n7. 再次切换第1个轨道:")
    controller.toggle_track_mute(1)
    controller.list_audio_tracks()
    
    print(f"\n=== 演示完成 ===")
    print("pymiere 音频轨道静音功能完全正常工作!")
    print("关键发现: setMute() 方法需要整数参数 (1=静音, 0=取消静音)")

def quick_mute_demo():
    """快速静音演示"""
    
    controller = AudioMuteController()
    
    if controller.connect() and controller.set_sequence("001"):
        print("\n=== 快速静音演示 ===")
        
        # 静音所有轨道
        print("静音所有轨道...")
        controller.mute_all_tracks()
        
        # 等待一下
        import time
        time.sleep(1)
        
        # 取消静音所有轨道
        print("\n取消静音所有轨道...")
        controller.unmute_all_tracks()
        
        print("\n快速演示完成!")

if __name__ == "__main__":
    print("Pymiere 音频轨道静音控制 - 工作版本")
    print("1. 完整演示")
    print("2. 快速演示")
    
    # 运行完整演示
    demo_working_audio_mute()