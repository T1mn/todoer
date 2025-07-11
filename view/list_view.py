from PyQt5.QtWidgets import QListView
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QMouseEvent


class TodoListView(QListView):
    """
    一个自定义的 QListView，专门用于显示待办事项。
    这个类方便未来扩展特定功能，例如自定义上下文菜单、拖放排序等。
    """
    
    # 定义信号：当项目被双击时发射
    item_double_clicked = pyqtSignal(QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_stylesheet()

    def _apply_stylesheet(self):
        """应用此控件专属的样式表"""
        self.setStyleSheet("""
            QListView {
                background-color: #2E2E2E;
                border-radius: 4px;
            }
        """)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """处理双击事件，切换项目完成状态"""
        index = self.indexAt(event.pos())
        if index.isValid():
            self.item_double_clicked.emit(index)
        super().mouseDoubleClickEvent(event) 