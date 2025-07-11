from PyQt5.QtWidgets import QListView, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt
from PyQt5.QtGui import QMouseEvent, QKeyEvent


class TodoListView(QListView):
    """
    一个自定义的 QListView，专门用于显示待办事项。
    支持右键菜单、Delete键删除和圆角样式设计。
    """
    
    # 定义信号：当项目被双击时发射
    item_double_clicked = pyqtSignal(QModelIndex)
    # 新增信号：右键菜单操作
    delete_item_requested = pyqtSignal(QModelIndex)
    show_info_requested = pyqtSignal(QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_stylesheet()

    def _apply_stylesheet(self):
        """应用圆角样式表"""
        self.setStyleSheet("""
            QListView {
                background-color: #2E2E2E;
                border-radius: 8px;
                border: 1px solid #444444;
                padding: 5px;
            }
            QListView::item {
                border-radius: 4px;
                padding: 2px;
                margin: 1px;
            }
            QListView::item:selected {
                background-color: #555555;
                border-radius: 4px;
            }
        """)

    def contextMenuEvent(self, event):
        """处理右键菜单事件，增强错误处理"""
        try:
            index = self.indexAt(event.pos())
            if not index.isValid():
                return

            # 确保索引有效性
            if not index.model() or index.row() < 0:
                return

            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #3E3E3E;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    color: #E0E0E0;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 6px 20px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
            """)

            # 添加查看详细信息选项
            info_action = QAction("📋 查看详细信息", self)
            info_action.triggered.connect(lambda checked, idx=index: self.show_info_requested.emit(idx))
            menu.addAction(info_action)

            menu.addSeparator()

            # 添加删除选项
            delete_action = QAction("🗑️ 删除项目", self)
            delete_action.triggered.connect(lambda checked, idx=index: self.delete_item_requested.emit(idx))
            menu.addAction(delete_action)

            # 安全地显示菜单
            menu.exec_(event.globalPos())
            
        except Exception as e:
            print(f"右键菜单处理错误: {e}")

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件，支持Delete键删除，增强错误处理"""
        try:
            if event.key() == Qt.Key_Delete:
                current_index = self.currentIndex()
                if current_index.isValid() and current_index.model():
                    # 确保索引有效后再发射信号
                    if current_index.row() >= 0 and current_index.row() < current_index.model().rowCount():
                        self.delete_item_requested.emit(current_index)
                    else:
                        print(f"Delete键：索引无效 - row: {current_index.row()}")
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"键盘事件处理错误: {e}")
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """处理双击事件，切换项目完成状态"""
        index = self.indexAt(event.pos())
        if index.isValid():
            self.item_double_clicked.emit(index)
        super().mouseDoubleClickEvent(event) 