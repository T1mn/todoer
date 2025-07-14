from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QComboBox, QPushButton, QFrame)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent
import os
from view.utils import load_stylesheet

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
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self._create_title(layout)
        self._create_input_section(layout)
        self._create_category_section(layout)
        self._create_buttons(layout)
        
        self.setLayout(layout)
        self.event_input.setFocus()
    
    def _create_title(self, layout):
        """创建标题部分"""
        if self.duration_minutes > 0:
            title_text = f"📝 {self.duration_minutes}分钟专注时间结束"
        else:
            title_text = "📝 记录完成的事情"
        
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        hint_label = QLabel("请记录您刚才完成的事情：")
        hint_label.setObjectName("hint")
        layout.addWidget(hint_label)
    
    def _create_input_section(self, layout):
        """创建输入区域"""
        self.event_input = QTextEdit()
        self.event_input.setPlaceholderText("例如：完成了Python项目的Timer模块开发\n\n按Ctrl+Enter快速提交")
        self.event_input.setObjectName("eventInput")
        self.event_input.setMaximumHeight(100)
        layout.addWidget(self.event_input)
    
    def _create_category_section(self, layout):
        """创建类别选择区域"""
        category_layout = QHBoxLayout()
        category_label = QLabel("类别:")
        category_label.setObjectName("categoryLabel")
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "工作 (work)", "学习 (study)", 
            "生活 (life)", "其他 (other)"
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
    
    def _create_buttons(self, layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        skip_btn = QPushButton("跳过记录")
        skip_btn.setObjectName("skipButton")
        skip_btn.clicked.connect(self._skip_record)
        
        save_btn = QPushButton("保存记录")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self._save_record)
        save_btn.setDefault(True)
        
        button_layout.addWidget(skip_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
    
    def _save_record(self):
        """保存事件记录"""
        event_text = self.event_input.toPlainText().strip()
        if not event_text:
            self.event_input.setFocus()
            return
        
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
        elif (event.modifiers() & Qt.KeyboardModifier.ControlModifier 
              and event.key() == Qt.Key.Key_Return):
            self._save_record()
        else:
            super().keyPressEvent(event)
    
    def _apply_styles(self):
        """应用样式"""
        style_path = os.path.join(os.path.dirname(__file__), 
                                 "..", "assets", "styles", "dark_theme.qss")
        self.setStyleSheet(load_stylesheet(style_path)) 