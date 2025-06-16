import time
import random
import threading
import os
import sys
import msvcrt  # Windows下键盘输入检测
import json  # 用于配置文件读写
import numpy as np  # 用于正态分布采样
from datetime import datetime, timedelta
import pygame  # 添加pygame库

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后的环境"""
    try:
        # PyInstaller会创建临时目录并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境下使用当前目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class ConfigManager:
    """配置管理类，用于保存和加载自定义设置"""
    
    def __init__(self):
        self.config_file = "focus_timer_configs.json"
        self.configs = self.load_configs()
    
    def load_configs(self):
        """加载已保存的配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"[WARNING] 加载配置文件失败: {e}")
            return {}
    
    def save_configs(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[ERROR] 保存配置文件失败: {e}")
            return False
    
    def save_config(self, name, settings):
        """保存一个配置"""
        # 添加保存时间戳
        settings['saved_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.configs[name] = settings
        return self.save_configs()
    
    def get_config(self, name):
        """获取指定名称的配置"""
        return self.configs.get(name)
    
    def list_configs(self):
        """列出所有已保存的配置"""
        return list(self.configs.keys())
    
    def delete_config(self, name):
        """删除指定配置"""
        if name in self.configs:
            del self.configs[name]
            return self.save_configs()
        return False

class FocusTimer:
    def __init__(self, mode="default", custom_settings=None):
        self.is_running = False
        self.session_start_time = None
        self.total_focus_time = 0  # 累计专注时间（分钟）
        self.is_resting = False
        self.is_paused = False  # 暂停状态
        self.pause_start_time = None  # 暂停开始时间
        self.total_pause_time = 0  # 总暂停时间
        self.mode = mode
        self.should_return_to_menu = False  # 是否返回主菜单
        
        # 初始化pygame音频
        pygame.mixer.init()
        
        # 默认音效文件路径 - 使用资源路径函数
        default_sounds = {
            "work_start": get_resource_path("work.mp3"),
            "short_rest": get_resource_path("small_rest.mp3"),
            "long_rest": get_resource_path("big_rest.mp3")
        }
        
        # 根据模式设置参数
        if mode == "test":
            self.max_focus_time = 6  # 测试模式：6秒后长休息
            self.short_rest_time = 1  # 测试模式：1秒短休息
            self.long_rest_time = 2   # 测试模式：2秒长休息
            self.min_focus_time = 1.0  # 测试模式：最小1秒
            self.max_single_focus_time = 2.0  # 测试模式：最大2秒
            self.focus_distribution = "uniform"  # 测试模式：均匀分布
            self.focus_mean = 1.5  # 正态分布均值（如果使用正态分布）
            self.focus_std = 0.3   # 正态分布标准差（如果使用正态分布）
            self.sounds = default_sounds
            print("[TEST] 测试模式启动 - 所有时间已缩短")
        elif mode == "custom" and custom_settings:
            # 自定义模式使用用户设置
            self.max_focus_time = custom_settings.get("max_focus_time", 90)
            self.short_rest_time = custom_settings.get("short_rest_time", 10)
            self.long_rest_time = custom_settings.get("long_rest_time", 20 * 60)
            
            # 自定义专注时间区间设置
            self.min_focus_time = custom_settings.get("min_focus_time", 3.0)
            self.max_single_focus_time = custom_settings.get("max_single_focus_time", 5.0)
            self.focus_distribution = custom_settings.get("focus_distribution", "uniform")
            self.focus_mean = custom_settings.get("focus_mean", 4.0)
            self.focus_std = custom_settings.get("focus_std", 0.8)
            
            # 处理自定义音效路径
            custom_sounds = custom_settings.get("sounds", {})
            self.sounds = {}
            for key, path in custom_sounds.items():
                if os.path.isabs(path):
                    # 如果是绝对路径，直接使用
                    self.sounds[key] = path
                else:
                    # 如果是相对路径，使用资源路径函数
                    self.sounds[key] = get_resource_path(path)
            
            # 确保所有必需的音效都有值
            for key, default_path in default_sounds.items():
                if key not in self.sounds:
                    self.sounds[key] = default_path
                    
            print("[CUSTOM] 自定义模式启动")
        else:
            # 默认模式
            self.max_focus_time = 90  # 正常模式：90分钟后长休息
            self.short_rest_time = 10  # 正常模式：10秒短休息
            self.long_rest_time = 20 * 60  # 正常模式：20分钟长休息
            self.min_focus_time = 3.0  # 默认模式：最小3分钟
            self.max_single_focus_time = 5.0  # 默认模式：最大5分钟
            self.focus_distribution = "uniform"  # 默认模式：均匀分布
            self.focus_mean = 4.0  # 正态分布均值
            self.focus_std = 0.8   # 正态分布标准差
            self.sounds = default_sounds
            print("[DEFAULT] 默认模式启动")

    def play_bell(self, event_type="default"):
        """播放不同类型的铃声"""
        try:
            sound_file = self.sounds.get(event_type)
            if sound_file and os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                # 等待音效播放完成
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                # 备用文字提示
                if sound_file:
                    print(f"[WARNING] 音效文件未找到: {sound_file}")
                if event_type == "work_start":
                    print("[BELL] 开始工作铃声！")
                elif event_type == "short_rest":
                    print("[BELL] 小休息铃声！")
                elif event_type == "long_rest":
                    print("[BELL] 大休息铃声！")
                else:
                    print("[BELL] 铃声响起！")
        except Exception as e:
            print(f"播放音效时出错: {e}")
            # 备用文字提示
            if event_type == "work_start":
                print("[BELL] 开始工作铃声！")
            elif event_type == "short_rest":
                print("[BELL] 小休息铃声！")
            elif event_type == "long_rest":
                print("[BELL] 大休息铃声！")
            else:
                print("[BELL] 铃声响起！")
    
    def get_random_focus_time(self):
        """获取随机专注时间（支持自定义区间和分布模式）"""
        if self.focus_distribution == "normal":
            # 正态分布采样
            while True:
                focus_time = np.random.normal(self.focus_mean, self.focus_std)
                # 确保生成的时间在合理范围内
                if self.min_focus_time <= focus_time <= self.max_single_focus_time:
                    return round(focus_time, 1)
                # 如果超出范围，重新采样（避免无限循环，最多尝试100次）
                # 如果100次都失败，回退到均匀分布
                for _ in range(100):
                    focus_time = np.random.normal(self.focus_mean, self.focus_std)
                    if self.min_focus_time <= focus_time <= self.max_single_focus_time:
                        return round(focus_time, 1)
                # 回退到均匀分布
                break
        
        # 均匀分布采样（默认或回退方案）
        focus_time = random.uniform(self.min_focus_time, self.max_single_focus_time)
        return round(focus_time, 1)
    
    def print_time_info(self, message, remaining_time=None):
        """打印时间信息"""
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{current_time}] {message}")
        if remaining_time:
            print(f"剩余时间: {remaining_time}")
        print("-" * 50)
    
    def check_for_pause_input(self):
        """检查是否有暂停/恢复输入（Windows系统）"""
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            if key == 'p':  # 按P键暂停/恢复
                return True
        return False

    def handle_pause(self):
        """处理暂停/恢复逻辑"""
        if self.is_paused:
            # 当前是暂停状态，恢复计时
            if self.pause_start_time:
                pause_duration = time.time() - self.pause_start_time
                self.total_pause_time += pause_duration
                self.pause_start_time = None
            self.is_paused = False
            print("\n[RESUME] 计时恢复！按 P 键暂停")
        else:
            # 当前是运行状态，暂停计时
            self.is_paused = True
            self.pause_start_time = time.time()
            print("\n[PAUSE] 计时已暂停！按 P 键恢复计时")

    def countdown(self, total_seconds, message_prefix=""):
        """倒计时显示（支持暂停/恢复）"""
        # 将浮点数秒转换为整数
        total_seconds = int(total_seconds)
        remaining_seconds = total_seconds
        
        print(f"\n提示：计时过程中按 P 键可暂停/恢复")
        
        while remaining_seconds > 0:
            if not self.is_running:
                return False
            
            # 检查是否有暂停输入
            if self.check_for_pause_input():
                self.handle_pause()
            
            # 如果暂停，不减少时间，继续循环
            if self.is_paused:
                time.sleep(0.1)  # 短暂休眠避免CPU占用过高
                continue
            
            mins, secs = divmod(remaining_seconds, 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"\r{message_prefix}{timer} [P:暂停]", end="", flush=True)
            
            time.sleep(1)
            remaining_seconds -= 1
        
        print()  # 换行
        return True
    
    def short_rest(self):
        """短休息"""
        self.is_resting = True
        rest_time = self.short_rest_time
        self.print_time_info(f"[REST] 开始{rest_time}秒休息时间...")
        self.play_bell("short_rest")  # 小休息音效
        
        if self.countdown(rest_time, "休息时间: "):
            self.play_bell("work_start")  # 工作开始音效
            self.print_time_info("[FOCUS] 休息结束，继续专注！")
        
        self.is_resting = False
    
    def long_rest(self):
        """长休息"""
        self.is_resting = True
        rest_time = self.long_rest_time
        if self.mode == "test":
            self.print_time_info(f"[LONG REST] 开始{rest_time}秒大休息时间！")
        else:
            self.print_time_info(f"[LONG REST] 开始{rest_time//60}分钟大休息时间！")
        self.play_bell("long_rest")  # 大休息音效
        
        if self.countdown(rest_time, "大休息时间: "):
            self.play_bell("work_start")  # 工作开始音效
            self.print_time_info("[NEW CYCLE] 大休息结束，开始新的专注循环！")
        
        self.is_resting = False
        self.total_focus_time = 0  # 重置累计时间
    
    def focus_session(self):
        """一次专注会话"""
        focus_time = self.get_random_focus_time()
        
        if self.mode == "test":
            self.print_time_info(f"[FOCUS] 开始 {focus_time} 秒专注时间")
            countdown_seconds = focus_time
        else:
            self.print_time_info(f"[FOCUS] 开始 {focus_time} 分钟专注时间")
            countdown_seconds = focus_time * 60
        
        if self.countdown(countdown_seconds, "专注时间: "):
            self.total_focus_time += focus_time
            if self.mode == "test":
                self.print_time_info(f"[DONE] 专注时间结束！累计专注: {self.total_focus_time:.1f} 秒")
            else:
                self.print_time_info(f"[DONE] 专注时间结束！累计专注: {self.total_focus_time:.1f} 分钟")
            return True
        return False
    
    def run(self):
        """运行主程序"""
        self.is_running = True
        self.session_start_time = datetime.now()
        
        print("[START] 专注程序启动！")
        if self.mode != "test":
            print("按 Ctrl+C 可以随时停止程序")
            print("计时过程中按 P 键可以暂停/恢复")
        print("=" * 50)
        
        cycle_count = 0  # 大周期计数器
        
        try:
            while self.is_running:
                # 检查是否需要长休息
                if self.total_focus_time >= self.max_focus_time:
                    cycle_count += 1
                    if self.mode == "test":
                        print(f"\n[CYCLE] 完成第 {cycle_count} 个大周期")
                    self.long_rest()
                    
                    # 测试模式下，完成2个大周期后自动停止
                    if self.mode == "test" and cycle_count >= 2:
                        print(f"\n[SUCCESS] 测试完成！成功完成 {cycle_count} 个大周期")
                        break
                    continue
                
                # 进行专注会话
                if self.focus_session():
                    # 专注完成后进行短休息
                    self.short_rest()
                else:
                    # 用户中断了专注
                    break
                    
        except KeyboardInterrupt:
            self.stop()
        
        if self.mode == "test":
            print(f"[END] 测试结束，共完成 {cycle_count} 个大周期")
    
    def stop(self):
        """停止程序"""
        self.is_running = False
        if self.session_start_time:
            # 如果当前处于暂停状态，结束暂停计时
            if self.is_paused and self.pause_start_time:
                pause_duration = time.time() - self.pause_start_time
                self.total_pause_time += pause_duration
                self.is_paused = False
                self.pause_start_time = None
            
            total_session_time = datetime.now() - self.session_start_time
            hours, remainder = divmod(total_session_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            print(f"\n\n[REPORT] 本次会话统计:")
            print(f"   总时长: {hours:02d}:{minutes:02d}:{seconds:02d}")
            if self.total_pause_time > 0:
                pause_mins, pause_secs = divmod(int(self.total_pause_time), 60)
                print(f"   暂停时长: {pause_mins:02d}:{pause_secs:02d}")
            if self.mode == "test":
                print(f"   累计专注: {self.total_focus_time:.1f} 秒")
            else:
                print(f"   累计专注: {self.total_focus_time:.1f} 分钟")
            
            self.ask_for_next_action()

    def ask_for_next_action(self):
        """询问用户下一步操作"""
        print("\n" + "="*40)
        print("专注会话已结束！")
        print("="*40)
        
        while True:
            try:
                print("\n请选择下一步操作：")
                print("1. 返回主菜单")
                print("2. 退出程序")
                choice = input("请选择 (1-2): ").strip()
                
                if choice == "1":
                    self.should_return_to_menu = True
                    print("[INFO] 即将返回主菜单...")
                    break
                elif choice == "2":
                    self.should_return_to_menu = False
                    print("[BYE] 感谢使用专注程序，再见！")
                    break
                else:
                    print("[ERROR] 无效选择，请输入 1 或 2")
            except KeyboardInterrupt:
                self.should_return_to_menu = False
                print("\n[BYE] 程序已退出")
                break

def show_menu():
    """显示主菜单"""
    print("\n" + "="*60)
    print(">>> 专注计时器 <<<")
    print("="*60)
    print("请选择运行模式：")
    print("1. 默认模式 - 标准的番茄工作法时间设置")
    print("2. 测试模式 - 所有时间大幅缩短，用于快速测试")
    print("3. 自定义模式 - 自由设定时间间隔和音效路径")
    print("0. 退出程序")
    print("="*60)

def get_custom_settings():
    """获取自定义设置"""
    print("\n[CUSTOM] 自定义模式设置")
    print("提示：直接按回车键将使用默认值")
    print("-" * 40)
    
    custom_settings = {}
    
    # 设置最大专注时间（分钟）
    try:
        max_focus_input = input(f"设置专注循环总时长（分钟，默认90）: ").strip()
        if max_focus_input:
            custom_settings["max_focus_time"] = float(max_focus_input)
        else:
            custom_settings["max_focus_time"] = 90
    except ValueError:
        print("[WARNING] 输入无效，使用默认值90分钟")
        custom_settings["max_focus_time"] = 90
    
    # 设置短休息时间（秒）
    try:
        short_rest_input = input(f"设置短休息时长（秒，默认10）: ").strip()
        if short_rest_input:
            custom_settings["short_rest_time"] = float(short_rest_input)
        else:
            custom_settings["short_rest_time"] = 10
    except ValueError:
        print("[WARNING] 输入无效，使用默认值10秒")
        custom_settings["short_rest_time"] = 10
    
    # 设置长休息时间（分钟）
    try:
        long_rest_input = input(f"设置长休息时长（分钟，默认20）: ").strip()
        if long_rest_input:
            custom_settings["long_rest_time"] = float(long_rest_input) * 60
        else:
            custom_settings["long_rest_time"] = 20 * 60
    except ValueError:
        print("[WARNING] 输入无效，使用默认值20分钟")
        custom_settings["long_rest_time"] = 20 * 60
    
    # 设置短专注时间区间
    print("\n[FOCUS INTERVAL] 短专注时间区间设置")
    print("提示：这里设置每次专注的随机时间范围")
    
    # 设置最小专注时间
    try:
        min_focus_input = input(f"设置最小专注时长（分钟，默认3）: ").strip()
        if min_focus_input:
            custom_settings["min_focus_time"] = float(min_focus_input)
        else:
            custom_settings["min_focus_time"] = 3.0
    except ValueError:
        print("[WARNING] 输入无效，使用默认值3分钟")
        custom_settings["min_focus_time"] = 3.0
    
    # 设置最大专注时间
    try:
        max_focus_input = input(f"设置最大专注时长（分钟，默认5）: ").strip()
        if max_focus_input:
            custom_settings["max_single_focus_time"] = float(max_focus_input)
        else:
            custom_settings["max_single_focus_time"] = 5.0
        
        # 确保最大值大于最小值
        if custom_settings["max_single_focus_time"] <= custom_settings["min_focus_time"]:
            print("[WARNING] 最大专注时间必须大于最小专注时间，自动调整")
            custom_settings["max_single_focus_time"] = custom_settings["min_focus_time"] + 1.0
    except ValueError:
        print("[WARNING] 输入无效，使用默认值5分钟")
        custom_settings["max_single_focus_time"] = 5.0
    
    # 设置随机分布模式
    print("\n[DISTRIBUTION] 随机分布模式设置")
    print("1. 均匀分布 (uniform) - 在区间内随机均匀分布")
    print("2. 正态分布 (normal) - 以均值为中心的正态分布")
    
    while True:
        dist_choice = input("请选择分布模式 (1-2，默认1): ").strip()
        if dist_choice == "" or dist_choice == "1":
            custom_settings["focus_distribution"] = "uniform"
            break
        elif dist_choice == "2":
            custom_settings["focus_distribution"] = "normal"
            
            # 如果选择正态分布，需要设置均值和标准差
            try:
                mean_input = input(f"设置均值（分钟，默认{(custom_settings['min_focus_time'] + custom_settings['max_single_focus_time'])/2:.1f}）: ").strip()
                if mean_input:
                    custom_settings["focus_mean"] = float(mean_input)
                else:
                    custom_settings["focus_mean"] = (custom_settings["min_focus_time"] + custom_settings["max_single_focus_time"]) / 2
            except ValueError:
                print("[WARNING] 输入无效，使用计算的默认均值")
                custom_settings["focus_mean"] = (custom_settings["min_focus_time"] + custom_settings["max_single_focus_time"]) / 2
            
            try:
                std_input = input(f"设置标准差（分钟，默认0.8）: ").strip()
                if std_input:
                    custom_settings["focus_std"] = float(std_input)
                else:
                    custom_settings["focus_std"] = 0.8
            except ValueError:
                print("[WARNING] 输入无效，使用默认标准差0.8")
                custom_settings["focus_std"] = 0.8
            break
        else:
            print("[ERROR] 无效选择，请输入 1 或 2")
    
    # 设置音效文件路径
    print("\n[SOUND] 音效设置（输入音频文件路径，支持mp3/wav格式）")
    sounds = {}
    
    work_start_sound = input("工作开始音效路径（默认：work.mp3）: ").strip()
    sounds["work_start"] = work_start_sound if work_start_sound else "work.mp3"
    
    short_rest_sound = input("短休息音效路径（默认：small_rest.mp3）: ").strip()
    sounds["short_rest"] = short_rest_sound if short_rest_sound else "small_rest.mp3"
    
    long_rest_sound = input("长休息音效路径（默认：big_rest.mp3）: ").strip()
    sounds["long_rest"] = long_rest_sound if long_rest_sound else "big_rest.mp3"
    
    custom_settings["sounds"] = sounds
    
    # 显示设置摘要
    print("\n[CONFIG] 您的自定义设置：")
    print(f"   专注循环总时长: {custom_settings['max_focus_time']} 分钟")
    print(f"   短休息时长: {custom_settings['short_rest_time']} 秒")
    print(f"   长休息时长: {custom_settings['long_rest_time']//60} 分钟")
    print(f"   短专注时间区间: {custom_settings['min_focus_time']:.1f} - {custom_settings['max_single_focus_time']:.1f} 分钟")
    print(f"   随机分布模式: {custom_settings['focus_distribution']}")
    if custom_settings['focus_distribution'] == 'normal':
        print(f"   正态分布均值: {custom_settings['focus_mean']:.1f} 分钟")
        print(f"   正态分布标准差: {custom_settings['focus_std']:.1f} 分钟")
    print(f"   工作开始音效: {sounds['work_start']}")
    print(f"   短休息音效: {sounds['short_rest']}")
    print(f"   长休息音效: {sounds['long_rest']}")
    
    confirm = input("\n确认使用以上设置？(y/n，默认y): ").strip().lower()
    if confirm == 'n' or confirm == 'no':
        print("已取消，返回主菜单")
        return None
    
    # 询问是否保存配置
    save_config = input("\n是否保存此配置以便下次使用？(y/n，默认n): ").strip().lower()
    if save_config == 'y' or save_config == 'yes':
        config_manager = ConfigManager()
        while True:
            config_name = input("请输入配置名称: ").strip()
            if not config_name:
                print("[WARNING] 配置名称不能为空")
                continue
            
            # 检查是否已存在同名配置
            if config_name in config_manager.list_configs():
                overwrite = input(f"配置 '{config_name}' 已存在，是否覆盖？(y/n): ").strip().lower()
                if overwrite != 'y' and overwrite != 'yes':
                    continue
            
            # 保存配置
            if config_manager.save_config(config_name, custom_settings.copy()):
                print(f"[SUCCESS] 配置 '{config_name}' 保存成功！")
            else:
                print(f"[ERROR] 配置 '{config_name}' 保存失败")
            break
    
    return custom_settings

def show_custom_mode_menu():
    """显示自定义模式菜单"""
    config_manager = ConfigManager()
    saved_configs = config_manager.list_configs()
    
    print("\n" + "="*60)
    print(">>> 自定义模式选择 <<<")
    print("="*60)
    print("请选择操作：")
    print("1. 创建新的自定义配置")
    
    if saved_configs:
        print("2. 加载已保存的配置")
        print("3. 管理已保存的配置")
    
    print("0. 返回主菜单")
    print("="*60)
    
    while True:
        try:
            if saved_configs:
                choice = input("\n请选择 (0-3): ").strip()
                if choice in ["0", "1", "2", "3"]:
                    return choice
            else:
                choice = input("\n请选择 (0-1): ").strip()
                if choice in ["0", "1"]:
                    return choice
            
            print("[ERROR] 无效选择，请重新输入")
        except KeyboardInterrupt:
            return "0"

def load_saved_config():
    """加载已保存的配置"""
    config_manager = ConfigManager()
    saved_configs = config_manager.list_configs()
    
    if not saved_configs:
        print("\n[INFO] 暂无已保存的配置")
        return None
    
    print("\n[SAVED CONFIGS] 已保存的配置:")
    print("-" * 50)
    for i, config_name in enumerate(saved_configs, 1):
        config = config_manager.get_config(config_name)
        saved_time = config.get('saved_time', '未知时间')
        print(f"{i}. {config_name} (保存时间: {saved_time})")
    
    print("0. 返回上级菜单")
    print("-" * 50)
    
    while True:
        try:
            choice = input(f"\n请选择配置 (0-{len(saved_configs)}): ").strip()
            
            if choice == "0":
                return None
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(saved_configs):
                    config_name = saved_configs[choice_idx]
                    config = config_manager.get_config(config_name)
                    
                    # 显示配置详情
                    print(f"\n[CONFIG] 配置 '{config_name}' 详情:")
                    print(f"   专注循环总时长: {config['max_focus_time']} 分钟")
                    print(f"   短休息时长: {config['short_rest_time']} 秒")
                    print(f"   长休息时长: {config['long_rest_time']//60} 分钟")
                    print(f"   短专注时间区间: {config.get('min_focus_time', 3.0):.1f} - {config.get('max_single_focus_time', 5.0):.1f} 分钟")
                    print(f"   随机分布模式: {config.get('focus_distribution', 'uniform')}")
                    if config.get('focus_distribution') == 'normal':
                        print(f"   正态分布均值: {config.get('focus_mean', 4.0):.1f} 分钟")
                        print(f"   正态分布标准差: {config.get('focus_std', 0.8):.1f} 分钟")
                    sounds = config.get('sounds', {})
                    print(f"   工作开始音效: {sounds.get('work_start', 'work.mp3')}")
                    print(f"   短休息音效: {sounds.get('short_rest', 'small_rest.mp3')}")
                    print(f"   长休息音效: {sounds.get('long_rest', 'big_rest.mp3')}")
                    print(f"   保存时间: {config.get('saved_time', '未知时间')}")
                    
                    confirm = input(f"\n确认加载配置 '{config_name}'？(y/n，默认y): ").strip().lower()
                    if confirm != 'n' and confirm != 'no':
                        print(f"[SUCCESS] 已加载配置 '{config_name}'")
                        return config
                    return None
                else:
                    print("[ERROR] 无效选择，请重新输入")
            except ValueError:
                print("[ERROR] 请输入有效数字")
                
        except KeyboardInterrupt:
            return None

def manage_saved_configs():
    """管理已保存的配置"""
    config_manager = ConfigManager()
    saved_configs = config_manager.list_configs()
    
    if not saved_configs:
        print("\n[INFO] 暂无已保存的配置")
        time.sleep(1)
        return
    
    while True:
        print("\n[CONFIG MANAGEMENT] 配置管理")
        print("-" * 40)
        for i, config_name in enumerate(saved_configs, 1):
            config = config_manager.get_config(config_name)
            saved_time = config.get('saved_time', '未知时间')
            print(f"{i}. {config_name} (保存时间: {saved_time})")
        
        print("0. 返回上级菜单")
        print("-" * 40)
        print("操作说明：输入数字查看详情，输入 'd数字' 删除配置（如：d1）")
        
        try:
            choice = input(f"\n请选择操作 (0-{len(saved_configs)} 或 d1-d{len(saved_configs)}): ").strip().lower()
            
            if choice == "0":
                break
            
            # 删除操作
            if choice.startswith('d') and len(choice) > 1:
                try:
                    del_idx = int(choice[1:]) - 1
                    if 0 <= del_idx < len(saved_configs):
                        config_name = saved_configs[del_idx]
                        confirm = input(f"确认删除配置 '{config_name}'？(y/n): ").strip().lower()
                        if confirm == 'y' or confirm == 'yes':
                            if config_manager.delete_config(config_name):
                                print(f"[SUCCESS] 配置 '{config_name}' 已删除")
                                saved_configs = config_manager.list_configs()
                                if not saved_configs:
                                    print("[INFO] 所有配置已删除，返回上级菜单")
                                    break
                            else:
                                print(f"[ERROR] 删除配置 '{config_name}' 失败")
                    else:
                        print("[ERROR] 无效的配置编号")
                except ValueError:
                    print("[ERROR] 无效的删除命令格式")
                continue
            
            # 查看详情操作
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(saved_configs):
                    config_name = saved_configs[choice_idx]
                    config = config_manager.get_config(config_name)
                    
                    print(f"\n[CONFIG DETAILS] 配置 '{config_name}' 详情:")
                    print(f"   专注循环总时长: {config['max_focus_time']} 分钟")
                    print(f"   短休息时长: {config['short_rest_time']} 秒")
                    print(f"   长休息时长: {config['long_rest_time']//60} 分钟")
                    print(f"   短专注时间区间: {config.get('min_focus_time', 3.0):.1f} - {config.get('max_single_focus_time', 5.0):.1f} 分钟")
                    print(f"   随机分布模式: {config.get('focus_distribution', 'uniform')}")
                    if config.get('focus_distribution') == 'normal':
                        print(f"   正态分布均值: {config.get('focus_mean', 4.0):.1f} 分钟")
                        print(f"   正态分布标准差: {config.get('focus_std', 0.8):.1f} 分钟")
                    sounds = config.get('sounds', {})
                    print(f"   工作开始音效: {sounds.get('work_start', 'work.mp3')}")
                    print(f"   短休息音效: {sounds.get('short_rest', 'small_rest.mp3')}")
                    print(f"   长休息音效: {sounds.get('long_rest', 'big_rest.mp3')}")
                    print(f"   保存时间: {config.get('saved_time', '未知时间')}")
                    
                    input("\n按回车键继续...")
                else:
                    print("[ERROR] 无效选择，请重新输入")
            except ValueError:
                print("[ERROR] 请输入有效数字或删除命令")
                
        except KeyboardInterrupt:
            break

def main():
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择 (0-3): ").strip()
            
            if choice == "0":
                print("[BYE] 再见！")
                break
            elif choice == "1":
                # 默认模式
                timer = FocusTimer(mode="default")
                timer.run()
                # 检查是否需要返回主菜单
                if not timer.should_return_to_menu:
                    break
            elif choice == "2":
                # 测试模式
                timer = FocusTimer(mode="test")
                timer.run()
                # 检查是否需要返回主菜单
                if not timer.should_return_to_menu:
                    break
            elif choice == "3":
                # 自定义模式
                while True:
                    custom_choice = show_custom_mode_menu()
                    
                    if custom_choice == "0":
                        # 返回主菜单
                        break
                    elif custom_choice == "1":
                        # 创建新的自定义配置
                        custom_settings = get_custom_settings()
                        if custom_settings:
                            timer = FocusTimer(mode="custom", custom_settings=custom_settings)
                            timer.run()
                            # 检查是否需要返回主菜单
                            if not timer.should_return_to_menu:
                                return  # 退出整个程序
                        break  # 返回主菜单
                    elif custom_choice == "2":
                        # 加载已保存的配置
                        loaded_config = load_saved_config()
                        if loaded_config:
                            timer = FocusTimer(mode="custom", custom_settings=loaded_config)
                            timer.run()
                            # 检查是否需要返回主菜单
                            if not timer.should_return_to_menu:
                                return  # 退出整个程序
                        break  # 返回主菜单
                    elif custom_choice == "3":
                        # 管理已保存的配置
                        manage_saved_configs()
            else:
                print("[ERROR] 无效选择，请输入 0-3 之间的数字")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n[BYE] 程序已退出")
            break
        except Exception as e:
            print(f"[ERROR] 发生错误: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main() 