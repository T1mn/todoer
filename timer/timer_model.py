import json
import os
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication
from .event_model import EventModel

# 导入日志管理器  
try:
    from utils.logger import module_logger
    def log_timer(event_type: str, message: str):
        module_logger.log_timer_event(event_type, message)
except ImportError:
    # 如果导入失败，使用print作为备选
    def log_timer(event_type: str, message: str):
        print(f"[TIMER-{event_type}] {message}")

class TimerStatus(Enum):
    """计时器状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running" 
    PAUSED = "paused"
    FINISHED = "finished"

class TimerModel(QObject):
    """番茄时间计时器模型"""
    
    # 信号定义
    time_updated = pyqtSignal(int)           # 时间更新信号(剩余秒数)
    timer_finished = pyqtSignal()            # 计时完成信号
    status_changed = pyqtSignal(str)         # 状态变化信号
    event_record_requested = pyqtSignal(int) # 请求记录事件信号(持续分钟数)
    
    def __init__(self, config_file="timer_settings.json"):
        super().__init__()
        
        # 基本属性
        self.total_seconds = 900  # 默认15分钟
        self.remaining_seconds = 900
        self.status = TimerStatus.STOPPED
        self.config_file = config_file
        
        # 内部计时器
        self._qtimer = QTimer()
        self._qtimer.timeout.connect(self._update_time)
        self._qtimer.setInterval(1000)  # 1秒间隔
        
        # 预设时间（分钟转秒）
        self.preset_times = [300, 900, 1500, 2700]  # 5m, 15m, 25m, 45m
        
        # 集成事件模型
        self.event_model = EventModel()
        
        # 会话跟踪
        self._session_active = False
        
        # 加载配置
        self.load_settings()
    
    def set_timer(self, seconds: int):
        """设置计时器时间"""
        if self.status == TimerStatus.RUNNING:
            return False
            
        self.total_seconds = max(60, min(10800, seconds))  # 1分钟到3小时
        self.remaining_seconds = self.total_seconds
        self.status = TimerStatus.STOPPED
        
        self.time_updated.emit(self.remaining_seconds)
        self.status_changed.emit(self.status.value)
        self.save_settings()
        return True
    
    def start_timer(self):
        """开始计时"""
        if self.status in [TimerStatus.STOPPED, TimerStatus.PAUSED]:
            self.status = TimerStatus.RUNNING
            self._qtimer.start()
            
            # 如果是从停止状态开始，启动新的事件会话
            if not self._session_active:
                self.event_model.start_session()
                self._session_active = True
            
            self.status_changed.emit(self.status.value)
            log_timer("START", f"番茄时间开始: {self.remaining_seconds//60}分{self.remaining_seconds%60}秒")
            return True
        return False
    
    def pause_timer(self):
        """暂停计时"""
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED
            self._qtimer.stop()
            self.status_changed.emit(self.status.value)
            log_timer("PAUSE", f"番茄时间暂停: 剩余{self.remaining_seconds//60}分{self.remaining_seconds%60}秒")
            return True
        return False
    
    def stop_timer(self):
        """停止计时"""
        if self.status in [TimerStatus.RUNNING, TimerStatus.PAUSED]:
            self.status = TimerStatus.STOPPED
            self._qtimer.stop()
            
            # 计算已完成的时间
            completed_seconds = self.total_seconds - self.remaining_seconds
            completed_minutes = completed_seconds // 60
            
            # 重置计时器
            self.remaining_seconds = self.total_seconds
            self.time_updated.emit(self.remaining_seconds)
            self.status_changed.emit(self.status.value)
            
            # 如果有活动会话且完成时间大于1分钟，请求记录事件
            if self._session_active and completed_minutes >= 1:
                self.event_record_requested.emit(completed_minutes)
            
            self._session_active = False
            log_timer("STOP", "番茄时间停止")
            return True
        return False
    
    def _update_time(self):
        """内部时间更新方法"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.time_updated.emit(self.remaining_seconds)
        else:
            # 时间到达，完成计时
            self._qtimer.stop()
            self.status = TimerStatus.FINISHED
            self.status_changed.emit(self.status.value)
            
            # 计算完成的时间（应该等于总时间）
            completed_minutes = self.total_seconds // 60
            
            # 发射完成信号
            self.timer_finished.emit()
            
            # 请求记录事件
            if self._session_active:
                self.event_record_requested.emit(completed_minutes)
            
            self._session_active = False
            log_timer("FINISHED", "番茄时间完成！")
    
    def record_event(self, event_description: str, category: str = "default"):
        """记录完成的事件"""
        if self.event_model.current_session_start:
            event = self.event_model.end_session(event_description, category)
            return event
        else:
            log_timer("WARNING", "没有活动的事件会话")
            return None
    
    def get_today_summary(self) -> dict:
        """获取今日事件统计"""
        return self.event_model.get_daily_summary()
    
    def get_time_display(self) -> str:
        """获取时间显示格式"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_button_text(self) -> str:
        """获取按钮显示文本"""
        if self.status == TimerStatus.STOPPED:
            return f"Timer {self.total_seconds//60}m"
        elif self.status == TimerStatus.RUNNING:
            return f"⏰ {self.get_time_display()}"
        elif self.status == TimerStatus.PAUSED:
            return f"⏸ {self.get_time_display()}"
        elif self.status == TimerStatus.FINISHED:
            return "✅ 完成"
        return "Timer"
    
    def save_settings(self):
        """保存设置到配置文件"""
        try:
            settings = {
                "default_time": self.total_seconds,
                "preset_times": self.preset_times,
                "last_used_time": self.total_seconds
            }
            
            # 确保config目录存在
            config_dir = os.path.dirname(self.config_file) or "config"
            os.makedirs(config_dir, exist_ok=True)
            
            config_path = os.path.join(config_dir, os.path.basename(self.config_file))
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            log_timer("ERROR", f"保存计时器设置失败: {e}")
    
    def load_settings(self):
        """从配置文件加载设置"""
        try:
            config_path = os.path.join("config", os.path.basename(self.config_file))
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.total_seconds = settings.get("default_time", 900)
                self.remaining_seconds = self.total_seconds
                self.preset_times = settings.get("preset_times", [300, 900, 1500, 2700])
                log_timer("LOAD", f"加载计时器设置: {self.total_seconds//60}分钟")
        except Exception as e:
            log_timer("WARNING", f"加载计时器设置失败，使用默认值: {e}")
            self.total_seconds = 900
            self.remaining_seconds = 900 