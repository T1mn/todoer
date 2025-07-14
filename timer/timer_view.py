from PySide6.QtWidgets import (QPushButton, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSpinBox, QGridLayout, QFrame)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QKeyEvent

# 导入日志管理器  
try:
    from utils.logger import module_logger
    def log_view(action: str, details: str):
        module_logger.log_view_action(action, details)
except ImportError:
    def log_view(action: str, details: str):
        print(f"[TIMER-VIEW-{action}] {details}")

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


class TimerDialog(QDialog):
    """计时器设置和控制对话框"""
    
    # 信号定义
    time_set_requested = Signal(int)
    start_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_styles()
        
        # 当前状态
        self.current_status = "stopped"
    
    def _setup_ui(self):
        """设置用户界面"""
        # 1. 设置为无边框窗口，让Qt完全接管绘制
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # 保持旧的 setWindowTitle，它可能对某些辅助技术有用
        self.setWindowTitle("番茄时间设置") 
        self.setFixedSize(300, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 这个 QLabel 现在将作为我们的自定义标题栏
        title_label = QLabel("🍅 番茄时间")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # 时间显示 - 修复高度问题
        self.time_display = QLabel("25:00")
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setObjectName("timeDisplay")
        self.time_display.setMinimumHeight(60)  # 增加最小高度
        self.time_display.setMaximumHeight(80)  # 设置最大高度
        layout.addWidget(self.time_display)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)
        
        # 预设时间按钮
        preset_layout = QGridLayout()
        self.preset_buttons = []
        
        preset_times = [(5, "5m"), (15, "15m"), (25, "25m"), (45, "45m")]
        for i, (minutes, label) in enumerate(preset_times):
            btn = QPushButton(label)
            btn.setObjectName("presetButton")
            btn.clicked.connect(lambda checked, m=minutes: self._set_preset_time(m))
            self.preset_buttons.append(btn)
            preset_layout.addWidget(btn, 0, i)
        
        layout.addLayout(preset_layout)
        
        # 自定义时间设置
        custom_layout = QHBoxLayout()
        custom_label = QLabel("自定义:")
        custom_label.setObjectName("customLabel")
        
        self.custom_spinbox = QSpinBox()
        self.custom_spinbox.setRange(1, 180)
        self.custom_spinbox.setValue(25)
        self.custom_spinbox.setSuffix(" 分钟")
        self.custom_spinbox.setObjectName("customSpinbox")
        self.custom_spinbox.valueChanged.connect(self._on_custom_time_changed)
        
        custom_layout.addWidget(custom_label)
        custom_layout.addWidget(self.custom_spinbox, 1)
        layout.addLayout(custom_layout)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始")
        self.start_btn.setObjectName("startButton")
        self.start_btn.clicked.connect(self._on_start_clicked)  # 修改为自定义方法
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setObjectName("pauseButton")
        self.pause_btn.clicked.connect(self.pause_requested.emit)
        self.pause_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)
        
        # 隐藏按钮（不是关闭）
        hide_layout = QHBoxLayout()
        hide_layout.addStretch()
        hide_btn = QPushButton("隐藏")
        hide_btn.setObjectName("hideButton")
        hide_btn.clicked.connect(self._hide_dialog)  # 修改为隐藏而不是关闭
        hide_layout.addWidget(hide_btn)
        layout.addLayout(hide_layout)
        
        self.setLayout(layout)

    # 2. 添加鼠标事件，使无边框窗口可以被拖动
    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于窗口移动"""
        if event.button() == Qt.LeftButton:  # type: ignore
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于窗口移动"""
        if hasattr(self, 'old_pos') and self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        self.old_pos = None

    def _hide_dialog(self):
        """隐藏对话框而不是关闭"""
        self.hide()

    def _on_start_clicked(self):
        """处理开始按钮点击：启动计时器并隐藏对话框进入专注模式"""
        self.start_requested.emit()  # 发送启动信号
        log_view("timer_start_and_hide", "计时器启动并进入专注模式（对话框已隐藏）")
        self.hide()  # 立即隐藏对话框，进入专注执行模式
    
    def _set_preset_time(self, minutes: int):
        """设置预设时间"""
        self.custom_spinbox.setValue(minutes)
        self.time_set_requested.emit(minutes * 60)
    
    def _on_custom_time_changed(self, minutes: int):
        """自定义时间改变处理"""
        self.time_set_requested.emit(minutes * 60)
    
    def update_time_display(self, seconds: int):
        """更新时间显示"""
        minutes = seconds // 60
        secs = seconds % 60
        self.time_display.setText(f"{minutes:02d}:{secs:02d}")
    
    def update_status(self, status: str):
        """更新按钮状态"""
        self.current_status = status
        
        if status == "stopped":
            self.start_btn.setEnabled(True)
            self.start_btn.setText("开始")
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
        elif status == "running":
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
        elif status == "paused":
            self.start_btn.setEnabled(True)
            self.start_btn.setText("继续")
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        elif status == "finished":
            self.start_btn.setEnabled(True)
            self.start_btn.setText("重新开始")
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            self._hide_dialog()  # 修改为隐藏而不是关闭
        elif event.key() == Qt.Key.Key_Space:
            if self.current_status == "running":
                self.pause_requested.emit()
            elif self.current_status in ["stopped", "paused"]:
                self._on_start_clicked()  # 使用自定义方法，确保自动隐藏
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """重写关闭事件，改为隐藏"""
        event.ignore()  # 忽略关闭事件
        self.hide()     # 隐藏对话框
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2E2E2E;
                border-radius: 8px;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #E0E0E0;
                padding: 8px;
            }
            QLabel#timeDisplay {
                font-size: 28px;
                font-weight: bold;
                color: #4CAF50;
                background-color: #1E1E1E;
                border-radius: 8px;
                padding: 15px;
                border: 2px solid #4CAF50;
                min-height: 60px;
                max-height: 80px;
            }
            QFrame#separator {
                color: #555555;
                background-color: #555555;
                max-height: 1px;
            }
            QPushButton#presetButton {
                background-color: #4A4A4A;
                color: #E0E0E0;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                min-width: 50px;
            }
            QPushButton#presetButton:hover {
                background-color: #555555;
            }
            QPushButton#presetButton:pressed {
                background-color: #666666;
            }
            QLabel#customLabel {
                color: #BBBBBB;
                font-size: 11px;
            }
            QSpinBox#customSpinbox {
                background-color: #3E3E3E;
                color: #E0E0E0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton#startButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#startButton:hover {
                background-color: #45A049;
            }
            QPushButton#pauseButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#pauseButton:hover {
                background-color: #F57C00;
            }
            QPushButton#stopButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#stopButton:hover {
                background-color: #D32F2F;
            }
            QPushButton#hideButton {
                background-color: #555555;
                color: #E0E0E0;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton#hideButton:hover {
                background-color: #666666;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #777777;
            }
        """) 