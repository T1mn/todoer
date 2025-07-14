from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal

class TimerButton(QPushButton):
    """主界面的计时器按钮"""
    
    timer_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Timer 15m")
        self.setFixedHeight(25)
        self.setMinimumWidth(80)
        self.clicked.connect(self.timer_clicked.emit)
        self._apply_style()
    
    def update_display(self, text: str, status: str = "stopped"):
        """更新按钮显示"""
        self.setText(text)
        self._update_style(status)
    
    def _apply_style(self):
        """应用基础样式"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: #E0E0E0;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
    
    def _update_style(self, status: str):
        """根据状态更新样式"""
        colors = {
            "stopped": "#555555",
            "running": "#2E7D32", 
            "paused": "#F57C00",
            "finished": "#388E3C"
        }
        
        color = colors.get(status, "#555555")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #E0E0E0;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
            QPushButton:pressed {{
                background-color: {color}BB;
            }}
        """)
