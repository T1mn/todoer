from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QComboBox, QPushButton, QFrame)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent

class EventDialog(QDialog):
    """事件记录对话框"""
    
    # 信号定义
    event_recorded = Signal(str, str)  # (事件描述, 类别)
    
    def __init__(self, duration_minutes: int = 0, parent=None):
        super().__init__(parent)
        self.duration_minutes = duration_minutes
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("记录完成的事情")
        self.setFixedSize(400, 300)
        self.setModal(True)
        # 修改窗口标志，确保它作为子窗口而不是独立的顶级窗口
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        if self.duration_minutes > 0:
            title_text = f"📝 {self.duration_minutes}分钟专注时间结束"
        else:
            title_text = "📝 记录完成的事情"
        
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # 提示文本
        hint_label = QLabel("请记录您刚才完成的事情：")
        hint_label.setObjectName("hint")
        layout.addWidget(hint_label)
        
        # 事件描述输入
        self.event_input = QTextEdit()
        self.event_input.setPlaceholderText("例如：完成了Python项目的Timer模块开发\n\n按Ctrl+Enter快速提交")
        self.event_input.setObjectName("eventInput")
        self.event_input.setMaximumHeight(100)
        layout.addWidget(self.event_input)
        
        # 类别选择
        category_layout = QHBoxLayout()
        category_label = QLabel("类别:")
        category_label.setObjectName("categoryLabel")
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "工作 (work)",
            "学习 (study)", 
            "生活 (life)",
            "其他 (other)"
        ])
        self.category_combo.setObjectName("categoryCombo")
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo, 1)
        layout.addLayout(category_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 跳过按钮
        skip_btn = QPushButton("跳过记录")
        skip_btn.setObjectName("skipButton")
        skip_btn.clicked.connect(self._skip_record)
        
        # 保存按钮
        save_btn = QPushButton("保存记录")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self._save_record)
        save_btn.setDefault(True)
        
        button_layout.addWidget(skip_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置焦点到输入框
        self.event_input.setFocus()
    
    def _save_record(self):
        """保存事件记录"""
        event_text = self.event_input.toPlainText().strip()
        if not event_text:
            self.event_input.setFocus()
            return
        
        # 获取类别
        category_text = self.category_combo.currentText()
        category = category_text.split('(')[1].rstrip(')')
        
        self.event_recorded.emit(event_text, category)
        self.accept()
    
    def _skip_record(self):
        """跳过记录"""
        self.reject()
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Return:
            # Ctrl+Enter 快速提交
            self._save_record()
        else:
            super().keyPressEvent(event)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2E2E2E;
                border-radius: 10px;
                border: 2px solid #4CAF50;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #4CAF50;
                padding: 10px;
            }
            QLabel#hint {
                color: #BBBBBB;
                font-size: 12px;
                margin-bottom: 5px;
            }
            QTextEdit#eventInput {
                background-color: #3E3E3E;
                color: #E0E0E0;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                selection-background-color: #4CAF50;
            }
            QTextEdit#eventInput:focus {
                border-color: #4CAF50;
            }
            QLabel#categoryLabel {
                color: #BBBBBB;
                font-size: 12px;
                min-width: 50px;
            }
            QComboBox#categoryCombo {
                background-color: #3E3E3E;
                color: #E0E0E0;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 6px;
                font-size: 12px;
            }
            QComboBox#categoryCombo:focus {
                border-color: #4CAF50;
            }
            QComboBox#categoryCombo::drop-down {
                border: none;
            }
            QComboBox#categoryCombo::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #BBBBBB;
            }
            QFrame#separator {
                color: #555555;
                background-color: #555555;
                max-height: 1px;
            }
            QPushButton#saveButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton#saveButton:hover {
                background-color: #45A049;
            }
            QPushButton#saveButton:pressed {
                background-color: #3E8E41;
            }
            QPushButton#skipButton {
                background-color: #666666;
                color: #E0E0E0;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton#skipButton:hover {
                background-color: #777777;
            }
            QPushButton#skipButton:pressed {
                background-color: #555555;
            }
        """) 