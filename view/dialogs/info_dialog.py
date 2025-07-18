"""
项目信息对话框模块

提供统一的项目详细信息显示界面，支持多种BaseItem类型。
根据项目类型动态显示相应的字段信息。
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QKeyEvent

from model.base_item import BaseItem
from model.todo_model import TodoItem, Priority
from model.event_model import RecordItem


class InfoDialog(QDialog):
    """统一的项目信息对话框 - 支持多种BaseItem类型"""

    def __init__(self, item: BaseItem, parent=None):
        super().__init__(parent)
        self.item = item
        self._setup_ui()

    def _setup_ui(self):
        """根据项目类型设置界面"""
        self.setFixedSize(350, 300)  # 稍微增加高度适应不同类型
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        # 动态标题
        title_map = {"todo": "任务详细信息", "record": "记录详细信息"}
        title_label = QLabel(title_map.get(self.item.item_type, "项目详细信息"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)

        # 根据类型显示不同字段
        if self.item.item_type == "todo":
            self._add_todo_fields(layout)
        elif self.item.item_type == "record":
            self._add_record_fields(layout)

        # 关闭按钮
        self._add_close_button(layout)
        self.setLayout(layout)

    def _add_todo_fields(self, layout):
        """添加待办事项特有字段"""
        item = self.item  # 类型为 TodoItem
        
        self._add_info_row(layout, "任务内容", item.description)
        self._add_info_row(layout, "优先级", self._format_priority(item.priority))
        self._add_info_row(layout, "类别", self._format_category(item.category))
        self._add_info_row(layout, "截止日期", self._format_qdate(item.deadline))
        self._add_info_row(layout, "创建时间", self._format_datetime(item.created_time))
        self._add_info_row(layout, "完成状态", "已完成" if item.done else "未完成")
        
        if item.donetime:
            self._add_info_row(layout, "完成时间", self._format_qdate(item.donetime))
        
        if item.consume_time > 0:
            self._add_info_row(layout, "预估时间", f"{item.consume_time} 分钟")

    def _add_record_fields(self, layout):
        """添加时间记录特有字段"""
        item = self.item  # 类型为 RecordItem
        
        self._add_info_row(layout, "记录描述", item.description)
        self._add_info_row(layout, "类别", self._format_category(item.category))
        self._add_info_row(layout, "记录类型", item.event_type)
        self._add_info_row(layout, "创建时间", self._format_datetime(item.created_time))
        
        if item.start_time:
            self._add_info_row(layout, "开始时间", self._format_datetime(item.start_time))

        if item.end_time:
            self._add_info_row(layout, "结束时间", self._format_datetime(item.end_time))
        
        if item.duration_seconds > 0:
            duration_minutes = item.duration_seconds // 60
            duration_seconds = item.duration_seconds % 60
            self._add_info_row(layout, "持续时间", f"{duration_minutes}分{duration_seconds}秒")

    def _add_close_button(self, layout):
        """添加关闭按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setObjectName("closeButton")
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

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

    def _format_priority(self, priority: Priority) -> str:
        """格式化优先级显示"""
        return priority.display_name

    def _format_category(self, category: str) -> str:
        """格式化类别显示"""
        category_map = {
            "work": "工作",
            "life": "生活",
            "study": "学习",
            "default": "默认"
        }
        return category_map.get(category, "默认")

    def _format_qdate(self, date: QDate) -> str:
        """格式化QDate显示"""
        if not date:
            return "未设置"
        return date.toString("yyyy-MM-dd")

    def _format_datetime(self, dt) -> str:
        """格式化datetime显示"""
        if not dt:
            return "未设置"
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件，支持Esc键退出"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)

     