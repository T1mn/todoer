from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup
from PySide6.QtCore import Signal, Qt


class ListToggleButtons(QWidget):
    """
    Material Design风格的切换按钮组
    用于在Todo List和Time List之间切换
    """
    
    mode_changed = Signal(str)  # "todo" or "time"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "todo"
        self._setup_ui()
        self._apply_material_design_style()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置UI组件"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建按钮组确保互斥选择
        self.button_group = QButtonGroup(self)
        
        # Todo按钮
        self.todo_button = QPushButton("📝 Todo")
        self.todo_button.setCheckable(True)
        self.todo_button.setChecked(True)  # 默认选中
        self.todo_button.setObjectName("toggleButton")
        
        # Time按钮
        self.time_button = QPushButton("🕐 Time")
        self.time_button.setCheckable(True)
        self.time_button.setObjectName("toggleButton")
        
        # 添加到按钮组
        self.button_group.addButton(self.todo_button, 0)
        self.button_group.addButton(self.time_button, 1)
        
        # 添加到布局
        layout.addWidget(self.todo_button)
        layout.addWidget(self.time_button)
    
    def _apply_material_design_style(self):
        """应用Material Design样式"""
        self.setStyleSheet("""
            QPushButton#toggleButton {
                background-color: #424242;
                color: #E0E0E0;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
                min-height: 28px;
                min-width: 60px;
            }
            
            QPushButton#toggleButton:checked {
                background-color: #1976D2;
                color: #FFFFFF;
            }
            
            QPushButton#toggleButton:hover {
                background-color: #555555;
            }
            
            QPushButton#toggleButton:checked:hover {
                background-color: #1565C0;
            }
            
            QPushButton#toggleButton:pressed {
                background-color: #333333;
            }
            
            QPushButton#toggleButton:checked:pressed {
                background-color: #0D47A1;
            }
        """)
    
    def _connect_signals(self):
        """连接信号槽"""
        self.todo_button.clicked.connect(lambda: self._on_button_clicked("todo"))
        self.time_button.clicked.connect(lambda: self._on_button_clicked("time"))
    
    def _on_button_clicked(self, mode: str):
        """处理按钮点击事件"""
        if self.current_mode != mode:
            self.current_mode = mode
            self.mode_changed.emit(mode)
    
    def set_mode(self, mode: str):
        """程序化设置模式"""
        if mode == "todo":
            self.todo_button.setChecked(True)
        elif mode == "time":
            self.time_button.setChecked(True)
        
        if self.current_mode != mode:
            self.current_mode = mode
            self.mode_changed.emit(mode)
    
    def get_current_mode(self) -> str:
        """获取当前模式"""
        return self.current_mode 