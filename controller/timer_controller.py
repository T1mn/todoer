import subprocess
import os
from PySide6.QtCore import QObject
from model.timer_model import TimerModel, TimerStatus
from view.widgets.timer.timer_view import TimerDialog
from view.widgets.timer.timer_button import TimerButton
from .notification_handler import NotificationHandler
from .timer_event_handler import TimerEventHandler

# 导入日志管理器  
try:
    from utils.logger import module_logger
    def log_controller(action: str, details: str):
        module_logger.log_controller_action(action, details)
except ImportError:
    def log_controller(action: str, details: str):
        print(f"[TIMER-CONTROLLER-{action}] {details}")

class TimerController(QObject):
    """番茄时间控制器，协调模型、视图和辅助处理器"""
    
    def __init__(self, parent=None, user_id="default_user", key_path="config/brilliant-balm-465903-g3-e308e8638139.json"):
        super().__init__(parent)
        
        self.model = TimerModel(user_id, key_path)
        self.button = TimerButton()
        self.dialog = None
        
        # 初始化辅助处理器
        self.notification_handler = NotificationHandler()
        self.event_handler = TimerEventHandler(self.model)
        
        self._connect_signals()
        self._update_button_display()
        log_controller("init", "番茄时间控制器初始化完成")
    
    def _connect_signals(self):
        """连接模型和视图的信号"""
        self.model.time_updated.connect(self._on_time_updated)
        self.model.timer_finished.connect(self._on_timer_finished)
        self.model.status_changed.connect(self._on_status_changed)
        self.model.event_record_requested.connect(self.event_handler.request_event_record)
        self.button.timer_clicked.connect(self.show_timer_dialog)

    def get_timer_button(self):
        """获取计时器按钮实例"""
        return self.button
    
    def show_timer_dialog(self):
        """显示或创建计时器对话框"""
        if not self.dialog:
            self.dialog = TimerDialog()
            self._connect_dialog_signals()
        
        self._update_dialog_display()
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
        
    def _connect_dialog_signals(self):
        """连接计时器对话框的信号"""
        if self.dialog:
            self.dialog.time_set_requested.connect(self.model.set_timer)
            self.dialog.start_requested.connect(self.model.start_timer)
            self.dialog.pause_requested.connect(self.model.pause_timer)
            self.dialog.stop_requested.connect(self.model.stop_timer)
            self.dialog.upload_requested.connect(self._handle_upload_request)
            self.dialog.download_requested.connect(self._handle_download_request)

    def _on_time_updated(self, remaining_seconds: int):
        """处理时间更新事件"""
        self._update_button_display()
        if self.dialog and self.dialog.isVisible():
            self.dialog.update_time_display(remaining_seconds)
    
    def _on_status_changed(self, status: str):
        """处理状态变更事件"""
        self._update_button_display()
        if self.dialog and self.dialog.isVisible():
            self.dialog.update_status(status)
    
    def _on_timer_finished(self):
        """处理计时完成事件"""
        self._update_button_display()
        self.notification_handler.show_notification()
        self.notification_handler.play_notification_sound()
        
        self.model.reset_timer()
        self._update_dialog_display()

    def _handle_upload_request(self):
        """处理上传请求"""
        log_controller("cloud_sync", "开始上传番茄钟数据")
        try:
            if self.model.sync_upload():
                log_controller("cloud_sync", "上传成功")
            else:
                log_controller("cloud_sync", "上传失败")
        except Exception as e:
            log_controller("cloud_sync_exception", f"上传异常: {e}")

    def _handle_download_request(self):
        """处理下载请求"""
        log_controller("cloud_sync", "开始下载番茄钟数据")
        try:
            if self.model.sync_download():
                log_controller("cloud_sync", "下载成功")
                self._update_dialog_display()
            else:
                log_controller("cloud_sync", "下载失败")
        except Exception as e:
            log_controller("cloud_sync_exception", f"下载异常: {e}")
    
    def _update_button_display(self):
        """更新按钮的文本和状态显示"""
        text = self.model.get_button_text()
        self.button.update_display(text, self.model.status.value)
    
    def _update_dialog_display(self):
        """更新对话框的显示内容"""
        if self.dialog:
            self.dialog.update_time_display(self.model.remaining_seconds)
            self.dialog.update_status(self.model.status.value)
            self.dialog.controls.custom_spinbox.setValue(self.model.total_seconds // 60) 