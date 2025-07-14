from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QKeyEvent

from .timer_display import TimerDisplay
from .timer_controls import TimerControls
from view.utils import load_stylesheet
import os

class TimerDialog(QDialog):
    """计时器设置和控制对话框"""
    time_set_requested = Signal(int)
    start_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()
    upload_requested = Signal()
    download_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = "stopped"
        self._setup_ui()
        self._connect_signals()
        # 加载dark qss
        style_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "styles", "dark_theme.qss")
        self.setStyleSheet(load_stylesheet(style_path))

    def _setup_ui(self):
        """设置UI"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowTitle("番茄时间设置")
        self.setFixedSize(300, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel("🍅 番茄时间")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        self.time_display = TimerDisplay()
        layout.addWidget(self.time_display)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)

        self.controls = TimerControls()
        layout.addWidget(self.controls)

        hide_layout = QHBoxLayout()
        hide_layout.addStretch()
        self.upload_btn = QPushButton("上传云端")
        self.upload_btn.setObjectName("uploadButton")
        self.download_btn = QPushButton("下载云端")
        self.download_btn.setObjectName("downloadButton")
        hide_btn = QPushButton("隐藏")
        hide_btn.setObjectName("hideButton")
        hide_btn.clicked.connect(self.hide)
        hide_layout.addWidget(self.upload_btn)
        hide_layout.addWidget(self.download_btn)
        hide_layout.addWidget(hide_btn)
        layout.addLayout(hide_layout)

    def _connect_signals(self):
        """连接信号"""
        self.controls.time_set_requested.connect(self.time_set_requested)
        self.controls.start_requested.connect(self._on_start_clicked)
        self.controls.pause_requested.connect(self.pause_requested)
        self.controls.stop_requested.connect(self.stop_requested)
        self.upload_btn.clicked.connect(self.upload_requested)
        self.download_btn.clicked.connect(self.download_requested)

    def _on_start_clicked(self):
        """处理开始按钮点击"""
        self.start_requested.emit()
        self.hide()

    def update_time_display(self, seconds: int):
        """更新时间显示"""
        self.time_display.update_time_display(seconds)

    def update_status(self, status: str):
        """更新按钮状态"""
        self.current_status = status
        self.controls.update_status(status)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'old_pos') and self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key.Key_Space:
            if self.current_status == "running":
                self.pause_requested.emit()
            elif self.current_status in ["stopped", "paused"]:
                self._on_start_clicked()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide()