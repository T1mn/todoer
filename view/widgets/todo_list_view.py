from PySide6.QtWidgets import QListView, QMenu
from PySide6.QtCore import Signal, QModelIndex, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent, QAction


class TodoListView(QListView):
    """
    一个自定义的 QListView，专门用于显示待办事项。
    支持右键菜单、Delete键删除和圆角样式设计。
    """
    
    # 定义信号：当项目被双击时发射
    item_double_clicked = Signal(QModelIndex)
    # 新增信号：右键菜单操作
    delete_item_requested = Signal(QModelIndex)
    show_info_requested = Signal(QModelIndex)

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
            print(f"🖱️ [右键菜单调试] 获取索引: {index.row() if index.isValid() else 'INVALID'}")
            
            if not index.isValid():
                print("❌ [右键菜单调试] 索引无效，不显示菜单")
                return

            # 确保索引有效性
            if not index.model() or index.row() < 0:
                print("❌ [右键菜单调试] 模型或行号无效")
                return
            
            print(f"✅ [右键菜单调试] 有效索引，行号: {index.row()}")

            menu = QMenu(self)

            # 添加查看详细信息选项 - 修复：使用无参数连接
            info_action = QAction("📋 查看详细信息", self)
            info_action.triggered.connect(lambda: self._emit_show_info(index))
            menu.addAction(info_action)

            menu.addSeparator()

            # 添加删除选项 - 修复：使用无参数连接
            delete_action = QAction("🗑️ 删除项目", self)
            delete_action.triggered.connect(lambda: self._emit_delete_item(index))
            menu.addAction(delete_action)

            # 安全地显示菜单
            menu.exec(event.globalPos())
            
        except Exception as e:
            print(f"❌ [右键菜单调试] 右键菜单处理错误: {e}")

    def _emit_show_info(self, index):
        """发射查看详情信号"""
        print(f"📋 [右键菜单调试] 发射查看详情信号，索引: {index.row() if index.isValid() else 'INVALID'}")
        if index.isValid():
            self.show_info_requested.emit(index)
        else:
            print("❌ [右键菜单调试] 无法发射查看详情信号，索引无效")

    def _emit_delete_item(self, index):
        """发射删除项目信号"""
        print(f"🗑️ [右键菜单调试] 发射删除信号，索引: {index.row() if index.isValid() else 'INVALID'}")
        if index.isValid():
            self.delete_item_requested.emit(index)
        else:
            print("❌ [右键菜单调试] 无法发射删除信号，索引无效")

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件，支持Delete键删除，增强错误处理"""
        try:
            if event.key() == Qt.Key.Key_Delete:
                current_index = self.currentIndex()
                print(f"⌨️ [Delete键调试] 当前索引: {current_index.row() if current_index.isValid() else 'INVALID'}")
                
                if current_index.isValid() and current_index.model():
                    # 确保索引有效后再发射信号
                    if current_index.row() >= 0 and current_index.row() < current_index.model().rowCount():
                        print(f"✅ [Delete键调试] 发射删除信号，行号: {current_index.row()}")
                        self.delete_item_requested.emit(current_index)
                    else:
                        print(f"❌ [Delete键调试] 索引无效 - row: {current_index.row()}, rowCount: {current_index.model().rowCount()}")
                else:
                    print("❌ [Delete键调试] 索引或模型无效")
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"❌ [Delete键调试] 键盘事件处理错误: {e}")
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """处理双击事件，切换项目完成状态"""
        index = self.indexAt(event.pos())
        if index.isValid():
            self.item_double_clicked.emit(index)
        super().mouseDoubleClickEvent(event) 