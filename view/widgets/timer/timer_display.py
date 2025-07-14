from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class TimerDisplay(QLabel):
    """计时器时间显示标签"""
    def __init__(self, parent=None):
        super().__init__("25:00", parent)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("timeDisplay")
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)

    def update_time_display(self, seconds: int):
        """更新时间显示"""
        minutes = seconds // 60
        secs = seconds % 60
        self.setText(f"{minutes:02d}:{secs:02d}")
