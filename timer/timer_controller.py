import subprocess
import os
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QSystemTrayIcon, QApplication
from .timer_model import TimerModel, TimerStatus
from .timer_view import TimerButton, TimerDialog
from .event_dialog import EventDialog

# 导入日志管理器  
try:
    from utils.logger import module_logger
    def log_controller(action: str, details: str):
        module_logger.log_controller_action(action, details)
except ImportError:
    def log_controller(action: str, details: str):
        print(f"[TIMER-CONTROLLER-{action}] {details}")

class TimerController(QObject):
    """番茄时间控制器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化模型和视图
        self.model = TimerModel()
        self.button = TimerButton()
        self.dialog = None
        self.event_dialog = None
        
        # 连接信号
        self._connect_signals()
        
        # 初始化按钮显示
        self._update_button_display()
        
        log_controller("init", "番茄时间控制器初始化完成")
    
    def _connect_signals(self):
        """连接模型和视图信号"""
        # 模型信号
        self.model.time_updated.connect(self._on_time_updated)
        self.model.timer_finished.connect(self._on_timer_finished)
        self.model.status_changed.connect(self._on_status_changed)
        self.model.event_record_requested.connect(self._on_event_record_requested)
        
        # 按钮信号
        self.button.timer_clicked.connect(self.show_timer_dialog)
    
    def get_timer_button(self):
        """获取计时器按钮，供主界面使用"""
        return self.button
    
    def show_timer_dialog(self):
        """显示计时器对话框"""
        if self.dialog is None:
            self.dialog = TimerDialog()
            # 连接对话框信号
            self.dialog.time_set_requested.connect(self.model.set_timer)
            self.dialog.start_requested.connect(self.model.start_timer)
            self.dialog.pause_requested.connect(self.model.pause_timer)
            self.dialog.stop_requested.connect(self.model.stop_timer)
        
        # 更新对话框状态
        self.dialog.update_time_display(self.model.remaining_seconds)
        self.dialog.update_status(self.model.status.value)
        self.dialog.custom_spinbox.setValue(self.model.total_seconds // 60)
        
        # 显示对话框（如果隐藏了会重新显示）
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
    
    def _on_time_updated(self, remaining_seconds: int):
        """时间更新处理"""
        self._update_button_display()
        if self.dialog and self.dialog.isVisible():
            self.dialog.update_time_display(remaining_seconds)
    
    def _on_status_changed(self, status: str):
        """状态变化处理"""
        self._update_button_display()
        if self.dialog and self.dialog.isVisible():
            self.dialog.update_status(status)
    
    def _on_timer_finished(self):
        """计时完成处理"""
        self._update_button_display()
        self._show_notification()
        self._play_notification_sound()
        
        # 重置为停止状态
        self.model.remaining_seconds = self.model.total_seconds
        self.model.status = TimerStatus.STOPPED
        self._update_button_display()
        if self.dialog and self.dialog.isVisible():
            self.dialog.update_status("stopped")
            self.dialog.update_time_display(self.model.remaining_seconds)
    
    def _on_event_record_requested(self, duration_minutes: int):
        """处理事件记录请求"""
        log_controller("event_record_requested", f"请求记录事件: {duration_minutes}分钟")
        
        # 创建事件记录对话框，设置主应用窗口为父窗口
        if self.event_dialog:
            self.event_dialog.close()
        
        # 获取主应用窗口作为父窗口
        main_window = None
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if hasattr(widget, 'get_list_view'):  # 这是MainWindow的特征
                    main_window = widget
                    break
        
        self.event_dialog = EventDialog(duration_minutes, main_window)
        self.event_dialog.event_recorded.connect(self._on_event_recorded)
        
        # 显示对话框
        self.event_dialog.show()
        self.event_dialog.raise_()
        self.event_dialog.activateWindow()
    
    def _on_event_recorded(self, event_description: str, category: str):
        """处理事件记录完成"""
        try:
            event = self.model.record_event(event_description, category)
            if event:
                log_controller("event_recorded", f"事件记录成功: {event_description}")
                
                # 显示今日统计
                summary = self.model.get_today_summary()
                log_controller("event_recorded", f"今日统计: {summary['total_events']}个事件, {summary['total_duration_formatted']}")
            else:
                log_controller("event_recorded", "事件记录失败")
        except Exception as e:
            log_controller("event_recorded_exception", f"事件记录异常: {e}")
        
        # 清理对话框
        if self.event_dialog:
            self.event_dialog.close()
            self.event_dialog = None
    
    def _update_button_display(self):
        """更新按钮显示"""
        text = self.model.get_button_text()
        status = self.model.status.value
        self.button.update_display(text, status)
    
    def _show_notification(self):
        """显示Ubuntu兼容的系统通知"""
        try:
            # 方法1: 使用notify-send (Ubuntu标准方式)
            if self._is_notify_send_available():
                subprocess.run([
                    'notify-send',
                    '🍅 番茄时间',
                    '时间到！休息一下吧~\n\n请记录您刚才完成的事情',
                    '--urgency=normal',
                    '--expire-time=8000',
                    '--icon=dialog-information'
                ], check=False)
                log_controller("show_notification", "系统通知已发送 (notify-send)")
                return
            
            # 方法2: 使用Qt系统托盘通知 (备用方案)
            if QSystemTrayIcon.isSystemTrayAvailable():
                # 这里需要一个临时的系统托盘图标来发送通知
                app = QApplication.instance()
                if app:
                    tray = QSystemTrayIcon()
                    if tray.supportsMessages():
                        tray.show()
                        tray.showMessage(
                            "🍅 番茄时间",
                            "时间到！休息一下吧~\n请记录您刚才完成的事情",
                            QSystemTrayIcon.Information,
                            8000
                        )
                        log_controller("show_notification", "系统通知已发送 (Qt托盘)")
                        return
            
            # 方法3: 终端输出 (最后备用)
            print("\n" + "="*50)
            print("🍅 番茄时间完成！")
            print("时间到！休息一下吧~")
            print("请记录您刚才完成的事情")
            print("="*50 + "\n")
            
        except Exception as e:
            log_controller("show_notification_exception", f"发送通知失败: {e}")
            print("🍅 番茄时间完成！时间到！")
    
    def _play_notification_sound(self):
        """播放通知声音"""
        try:
            # Ubuntu兼容的声音播放方式
            sound_commands = [
                ['paplay', '/usr/share/sounds/alsa/Front_Right.wav'],  # PulseAudio
                ['aplay', '/usr/share/sounds/alsa/Front_Right.wav'],   # ALSA
                ['play', '/usr/share/sounds/sound-icons/bell.oga'],    # SoX
                ['speaker-test', '-t', 'sine', '-f', '800', '-l', '1'] # 蜂鸣器
            ]
            
            for cmd in sound_commands:
                try:
                    if subprocess.run(['which', cmd[0]], 
                                    capture_output=True, check=False).returncode == 0:
                        subprocess.run(cmd, capture_output=True, timeout=2, check=False)
                        log_controller("play_notification_sound", f"播放通知音: {cmd[0]}")
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            else:
                # 如果没有找到音频播放器，使用系统蜂鸣
                print('\a')  # ASCII蜂鸣字符
                print("🔔 系统蜂鸣提醒")
                log_controller("play_notification_sound", "系统蜂鸣提醒")
                
        except Exception as e:
            log_controller("play_notification_sound_exception", f"播放通知音失败: {e}")
    
    def _is_notify_send_available(self) -> bool:
        """检查notify-send是否可用"""
        try:
            result = subprocess.run(['which', 'notify-send'], 
                                  capture_output=True, check=False)
            return result.returncode == 0
        except FileNotFoundError:
            return False 