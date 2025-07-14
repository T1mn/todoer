from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QKeyEvent
from model.todo_model import TodoItem, Priority


class InfoDialog(QDialog):
    """显示待办事项详细信息的简洁对话框"""

    def __init__(self, item: TodoItem, parent=None):
        super().__init__(parent)
        self.item = item
        self._setup_ui()

    def _setup_ui(self):
        """设置简洁用户界面"""
        self.setFixedSize(350, 280)
        self.setModal(True)
        # 设置无边框无标题样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title_label = QLabel("任务详细信息")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)

        # 信息内容
        self._add_info_row(layout, "任务内容", self.item.text)
        self._add_info_row(layout, "优先级", self._format_priority())
        self._add_info_row(layout, "类别", self._format_category())
        self._add_info_row(layout, "截止日期", self._format_date(self.item.deadline))
        self._add_info_row(layout, "创建时间", self._format_date(self.item.createtime))
        self._add_info_row(layout, "完成状态", "已完成" if self.item.done else "未完成")
        
        if self.item.donetime:
            self._add_info_row(layout, "完成时间", self._format_date(self.item.donetime))
        
        if self.item.consume_time > 0:
            self._add_info_row(layout, "预估时间", self._format_time())

        # 关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setObjectName("closeButton")
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _add_info_row(self, layout, label_text: str, value_text: str):
        """添加信息行"""
        row_layout = QHBoxLayout()
        
        label = QLabel(f"{label_text}:")
        label.setObjectName("infoLabel")
        label.setMinimumWidth(70)
        
        value = QLabel(value_text if value_text else "未设置")
        value.setObjectName("infoValue")
        value.setWordWrap(True)
        
        row_layout.addWidget(label)
        row_layout.addWidget(value, 1)
        layout.addLayout(row_layout)

    def _format_priority(self) -> str:
        """格式化优先级显示"""
        priority_map = {
            Priority.URGENT: "紧急",
            Priority.HIGH: "高",
            Priority.MEDIUM: "中等", 
            Priority.LOW: "低"
        }
        return priority_map.get(self.item.priority, "中等")

    def _format_category(self) -> str:
        """格式化类别显示"""
        category_map = {
            "work": "工作",
            "life": "生活",
            "study": "学习",
            "default": "默认"
        }
        return category_map.get(self.item.category, "默认")

    def _format_date(self, date: QDate) -> str:
        """格式化日期显示"""
        if not date:
            return "未设置"
        return date.toString("yyyy-MM-dd")

    def _format_time(self) -> str:
        """格式化预估时间显示"""
        if self.item.consume_time > 0:
            return f"{self.item.consume_time} 分钟"
        return "未设置"

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件，支持Esc键退出"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)

     