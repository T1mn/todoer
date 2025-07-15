from PySide6.QtCore import Qt, Signal, QPoint, QModelIndex
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QStackedWidget
from PySide6.QtGui import QKeySequence, QShortcut

from view.widgets.ai_line_edit import AILineEdit
from view.widgets.todo_list_view import TodoListView
from view.widgets.time_list_view import TimeListView
from view.widgets.list_toggle_buttons import ListToggleButtons
from view.utils import load_stylesheet

class MainWindow(QWidget):
    """应用程序的主视图"""
    add_item_requested = Signal(str)
    ai_parse_requested = Signal(str)
    delete_item_requested = Signal(QModelIndex)
    toggle_item_requested = Signal(QModelIndex)
    sort_items_requested = Signal()
    save_requested = Signal()
    upload_requested = Signal()
    download_requested = Signal()
    
    def __init__(self, config: dict, event_model=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.event_model = event_model
        self.old_pos = None
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
        style = load_stylesheet("view/assets/styles/dark_theme.qss")
        self.setStyleSheet(style)

    def _center_on_secondary_screen(self):
        """将窗口移动到副显示器的右下角"""
        screens = QApplication.screens()
        if not screens:
            return
        
        primary_screen = screens[0].geometry()
        target_screen = screens[1].availableGeometry() if len(screens) > 1 else primary_screen
        
        self.move(target_screen.right() - self.width(), target_screen.bottom() - self.height())

    def _setup_widgets(self):
        """创建UI控件"""
        self.input_lineedit = AILineEdit()
        self.input_lineedit.setInputMethodHints(Qt.ImhNone)
        self.input_lineedit.setAttribute(Qt.WA_InputMethodEnabled, True)
        
        # 创建切换按钮
        self.toggle_buttons = ListToggleButtons()
        
        # 创建堆叠视图管理器
        self.list_stack = QStackedWidget()
        self.todo_list_view = TodoListView()
        self.time_list_view = TimeListView(self.event_model) if self.event_model else None
        
        self.list_stack.addWidget(self.todo_list_view)
        if self.time_list_view:
            self.list_stack.addWidget(self.time_list_view)
        
        # 保持向后兼容，list_view指向当前活动视图
        self.list_view = self.todo_list_view
        
        self.sort_btn = QPushButton('Sort')
        self.upload_btn = QPushButton('上传云端')
        self.download_btn = QPushButton('下载云端')
        
        self.status_bar = QWidget()
        self.status_bar.setObjectName("statusBar")
        self.status_bar.setFixedHeight(self.config['ui']['status_bar_height'])

    def _setup_layout(self):
        """设置UI布局"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 输入区域：AI输入框 + 切换按钮
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_lineedit, 1)  # 拉伸占主要空间
        input_layout.addWidget(self.toggle_buttons)
        
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.sort_btn)
        self.btn_layout.addWidget(self.upload_btn)
        self.btn_layout.addWidget(self.download_btn)
        
        self.main_layout.addWidget(self.status_bar)
        self.main_layout.addLayout(input_layout)
        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.list_stack)

    def add_widget_to_button_layout(self, widget, position):
        """向按钮布局中添加一个小部件"""
        self.btn_layout.insertWidget(position, widget)
        
    def _connect_signals(self):
        """连接内部控件的信号到视图的主信号"""
        self.input_lineedit.returnPressed.connect(self._on_add_item)
        self.input_lineedit.ai_parse_requested.connect(self.ai_parse_requested)
        
        # 新增切换按钮信号
        self.toggle_buttons.mode_changed.connect(self._on_mode_changed)
        
        self.sort_btn.clicked.connect(self.sort_items_requested)
        self.upload_btn.clicked.connect(self.upload_requested)
        self.download_btn.clicked.connect(self.download_requested)
        
        # 连接当前活动视图的信号
        self._connect_current_list_signals()

        quit_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        quit_shortcut.activated.connect(self._quit_application)

    def _quit_application(self):
        """强制退出整个应用程序"""
        self.close()
        app = QApplication.instance()
        if app:
            app.quit()

    def _on_add_item(self):
        """当输入框回车时，发射添加信号并清空输入"""
        text = self.input_lineedit.text()
        if text:
            self.add_item_requested.emit(text)
            self.input_lineedit.clear()

    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于窗口移动"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于窗口移动"""
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        self.old_pos = None

    def closeEvent(self, event):
        """重写关闭事件，确保应用程序正确退出"""
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

    def _on_mode_changed(self, mode: str):
        """处理模式切换"""
        if mode == "todo":
            self.list_stack.setCurrentWidget(self.todo_list_view)
            self.list_view = self.todo_list_view
        elif mode == "time" and self.time_list_view:
            self.list_stack.setCurrentWidget(self.time_list_view)
            self.list_view = self.time_list_view
        
        # 重新连接当前活动视图的信号
        self._connect_current_list_signals()
    
    def _connect_current_list_signals(self):
        """连接当前活动视图的信号"""
        # 断开之前的连接
        try:
            self.todo_list_view.item_double_clicked.disconnect()
            if self.time_list_view:
                self.time_list_view.item_double_clicked.disconnect()
        except:
            pass
        
        # 连接当前活动视图的信号
        current_view = self.list_stack.currentWidget()
        if current_view:
            current_view.item_double_clicked.connect(self.toggle_item_requested)

    def get_list_view(self):
        """获取当前活动的列表视图对象，供控制器使用"""
        return self.list_view