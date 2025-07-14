
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from model.timer_model import TimerModel
from view.dialogs.event_dialog import EventDialog

try:
    from utils.logger import module_logger
    def log_controller(action: str, details: str):
        module_logger.log_controller_action(action, details)
except ImportError:
    def log_controller(action: str, details: str):
        print(f"[TIMER-EVENT-{action}] {details}")

class TimerEventHandler(QObject):
    """处理计时器事件记录的辅助类"""
    
    def __init__(self, model: TimerModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.event_dialog = None

    def request_event_record(self, duration_minutes: int):
        """请求记录事件"""
        log_controller("event_record_requested", f"请求记录事件: {duration_minutes}分钟")
        
        if self.event_dialog:
            self.event_dialog.close()
        
        main_window = self._find_main_window()
        self.event_dialog = EventDialog(duration_minutes, main_window)
        self.event_dialog.event_recorded.connect(self.record_event)
        
        self.event_dialog.show()
        self.event_dialog.raise_()
        self.event_dialog.activateWindow()
        
    def record_event(self, event_description: str, category: str):
        """处理事件记录完成"""
        try:
            event = self.model.record_event(event_description, category)
            if event:
                log_controller("event_recorded", f"事件记录成功: {event_description}")
                self._log_today_summary()
            else:
                log_controller("event_recorded", "事件记录失败")
        except Exception as e:
            log_controller("event_recorded_exception", f"事件记录异常: {e}")
        
        self._cleanup_dialog()

    def _log_today_summary(self):
        """记录并打印今日统计"""
        summary = self.model.get_today_summary()
        log_controller("event_recorded", f"今日统计: {summary['total_events']}个事件, {summary['total_duration_formatted']}")

    def _cleanup_dialog(self):
        """清理对话框资源"""
        if self.event_dialog:
            self.event_dialog.close()
            self.event_dialog = None
            
    def _find_main_window(self):
        """查找并返回主窗口实例"""
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if hasattr(widget, 'get_list_view'):  # MainWindow的特征
                    return widget
        return None 