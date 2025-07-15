from PySide6.QtWidgets import QListView, QMenu
from PySide6.QtCore import Signal, QModelIndex, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent, QAction


class BaseListView(QListView):
    """
    所有列表视图的基类
    遵循Google Material Design List组件规范
    提供统一的交互体验和视觉风格
    """
    
    # 统一的信号定义
    item_double_clicked = Signal(QModelIndex)
    delete_item_requested = Signal(QModelIndex)
    show_info_requested = Signal(QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_material_design_style()
        self._setup_context_menu()
        self._connect_signals()

    def _apply_material_design_style(self):
        """应用Material Design样式"""
        self.setStyleSheet("""
            QListView {
                background-color: #2E2E2E;
                border-radius: 8px;
                border: 1px solid #444444;
                padding: 8px;
                outline: none;
            }
            QListView::item {
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
                min-height: 40px;
            }
            QListView::item:selected {
                background-color: #1976D2;
                color: #FFFFFF;
            }
            QListView::item:hover {
                background-color: #424242;
            }
        """)

    def _setup_context_menu(self):
        """设置统一的右键菜单"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _connect_signals(self):
        """连接基础信号"""
        self.doubleClicked.connect(self.item_double_clicked.emit)

    def _show_context_menu(self, position):
        """显示右键菜单"""
        index = self.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self)
        
        # 查看详情
        info_action = QAction("查看详情", self)
        info_action.triggered.connect(lambda: self.show_info_requested.emit(index))
        menu.addAction(info_action)
        
        # 删除项目
        delete_action = QAction("删除(Delete)", self)
        delete_action.triggered.connect(lambda: self.delete_item_requested.emit(index))
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(position))

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件"""
        if event.key() == Qt.Key_Delete:
            current_index = self.currentIndex()
            if current_index.isValid():
                self.delete_item_requested.emit(current_index)
        else:
            super().keyPressEvent(event)

    def get_display_name(self) -> str:
        """返回列表的显示名称 - 子类应重写此方法"""
        return "列表"

    def get_empty_message(self) -> str:
        """返回空列表时的提示信息 - 子类应重写此方法"""
        return "暂无数据"

    def handle_empty_state(self):
        """处理空列表状态显示"""
        # 子类可以重写此方法来自定义空状态显示
        pass 