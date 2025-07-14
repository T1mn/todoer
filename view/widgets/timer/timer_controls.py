from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSpinBox, QLabel, QGridLayout
from PySide6.QtCore import Signal

class TimerControls(QWidget):
    """计时器控制按钮和设置"""
    time_set_requested = Signal(int)
    start_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 预设时间按钮
        preset_layout = QGridLayout()
        self.preset_buttons = []
        preset_times = [(5, "5m"), (15, "15m"), (25, "25m"), (45, "45m")]
        for i, (minutes, label) in enumerate(preset_times):
            btn = QPushButton(label)
            btn.setObjectName("presetButton")
            btn.clicked.connect(lambda checked=False, m=minutes: self._set_preset_time(m))
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
        custom_layout.addWidget(custom_label)
        custom_layout.addWidget(self.custom_spinbox, 1)
        layout.addLayout(custom_layout)

        # 控制按钮
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始")
        self.start_btn.setObjectName("startButton")
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setObjectName("pauseButton")
        self.pause_btn.setEnabled(False)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)

    def _connect_signals(self):
        """连接信号"""
        self.custom_spinbox.valueChanged.connect(self._on_custom_time_changed)
        self.start_btn.clicked.connect(self.start_requested.emit)
        self.pause_btn.clicked.connect(self.pause_requested.emit)
        self.stop_btn.clicked.connect(self.stop_requested.emit)

    def _set_preset_time(self, minutes: int):
        """设置预设时间"""
        self.custom_spinbox.setValue(minutes)
        self.time_set_requested.emit(minutes * 60)

    def _on_custom_time_changed(self, minutes: int):
        """自定义时间改变处理"""
        self.time_set_requested.emit(minutes * 60)

    def update_status(self, status: str):
        """更新按钮状态"""
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
