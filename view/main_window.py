from PySide6.QtCore import Qt, Signal, QPoint, QModelIndex
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QApplication
from PySide6.QtGui import QKeySequence, QKeyEvent, QShortcut
from .list_view import TodoListView


class AILineEdit(QLineEdit):
    """支持 AI 解析的自定义 QLineEdit"""
    ai_parse_requested = Signal(str)
    
    def keyPressEvent(self, event: QKeyEvent):
        """重写键盘事件处理，支持 Shift+Enter"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter：触发 AI 解析
                text = self.text()
                if text:
                    self.ai_parse_requested.emit(text)
                    self.clear()
                return  # 阻止事件继续传播
            else:
                # 普通 Enter：使用默认行为（会触发 returnPressed 信号）
                super().keyPressEvent(event)
        else:
            # 其他键：使用默认行为
            super().keyPressEvent(event)


class MainWindow(QWidget):
    """应用程序的主视图"""
    # 定义信号，用于与控制器通信
    add_item_requested = Signal(str)
    ai_parse_requested = Signal(str)  # 新增：AI 解析请求
    delete_item_requested = Signal(QModelIndex)
    toggle_item_requested = Signal(QModelIndex)  # 新增：切换项目完成状态
    sort_items_requested = Signal()
    save_requested = Signal()
    load_requested = Signal()
    
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        """初始化UI界面"""
        self._setup_window()
        self._setup_widgets()
        self._setup_layout()
        self._connect_signals()

    def _setup_window(self):
        """配置窗口属性"""
        ui_cfg = self.config['ui']
        self.setWindowOpacity(ui_cfg['opacity'])
        self.setWindowTitle('To-Do List')
        self.setGeometry(0, 0, ui_cfg['window_width'], ui_cfg['window_height'])
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self._center_on_secondary_screen()
        self._apply_stylesheet()

    def _apply_stylesheet(self):
        """应用暗色主题样式表"""
        self.setStyleSheet("""
            QWidget {
                background-color: #3C3C3C;
                color: #E0E0E0;
                border: none;
            }
            QLineEdit {
                background-color: #2E2E2E;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #555;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """)

    def _center_on_secondary_screen(self):
        """将窗口移动到副显示器的右下角"""
        screens = QApplication.screens()
        primary_screen = screens[0].geometry()
        
        target_screen = screens[1].availableGeometry() if len(screens) > 1 else primary_screen
        
        self.move(target_screen.right() - self.width(), target_screen.bottom() - self.height())


    def _setup_widgets(self):
        """创建UI控件"""
        self.input_lineedit = AILineEdit()  # 使用自定义的 AILineEdit
        
        # 启用输入法支持，允许中文输入
        self.input_lineedit.setInputMethodHints(Qt.ImhNone)
        self.input_lineedit.setAttribute(Qt.WA_InputMethodEnabled, True)
        
        self.list_view = TodoListView()
        self.load_btn = QPushButton('Load')
        # 在这里会通过控制器添加timer按钮
        self.sort_btn = QPushButton('Sort')
        self.status_bar = QWidget()
        self.status_bar.setFixedHeight(self.config['ui']['status_bar_height'])
        self.status_bar.setStyleSheet("background-color: gray;")

    def _setup_layout(self):
        """设置UI布局"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.sort_btn)
        
        self.main_layout.addWidget(self.status_bar)
        self.main_layout.addWidget(self.input_lineedit)
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addWidget(self.list_view)
        
    def _connect_signals(self):
        """连接内部控件的信号到视图的主信号"""
        self.input_lineedit.returnPressed.connect(self._on_add_item)
        self.input_lineedit.ai_parse_requested.connect(self._on_ai_parse_from_lineedit)  # 连接自定义信号
        self.load_btn.clicked.connect(self.load_requested)
        self.sort_btn.clicked.connect(self.sort_items_requested)
        
        # 连接列表视图的双击信号
        self.list_view.item_double_clicked.connect(self.toggle_item_requested)

        # 添加 Ctrl+W 退出快捷键
        quit_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        quit_shortcut.activated.connect(self._quit_application)

    def _on_ai_parse_from_lineedit(self, text: str):
        """从自定义 QLineEdit 接收 AI 解析请求"""
        self.ai_parse_requested.emit(text)

    def _on_ai_parse(self):
        """当 Shift+Enter 时，发射 AI 解析信号"""
        text = self.input_lineedit.text()
        if text:
            self.ai_parse_requested.emit(text)
            self.input_lineedit.clear()

    def _quit_application(self):
        """强制退出整个应用程序"""
        self.close()  # 先关闭窗口
        # 添加类型守卫，消除Linter误报
        app = QApplication.instance()
        if app:
            app.quit()  # 现在Linter知道app不是None

    def _on_add_item(self):
        """当输入框回车时，发射添加信号并清空输入"""
        text = self.input_lineedit.text()
        if text:
            self.add_item_requested.emit(text)
            self.input_lineedit.clear()

    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于窗口移动"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于窗口移动"""
        if hasattr(self, 'old_pos') and self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def closeEvent(self, event):
        """重写关闭事件，确保应用程序正确退出"""
        # 添加类型守卫，消除Linter误报
        app = QApplication.instance()
        if app:
            app.quit()
        event.accept()

    def show_toggle(self):
        """切换窗口的显示和隐藏状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show() 

    def get_list_view(self):
        """获取列表视图对象，供控制器使用"""
        return self.list_view 