import sys
from PyQt5.QtCore import Qt, QPoint, QRect, QSettings, QSize, QDate, pyqtSignal, QThread, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QDesktopWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QCheckBox, QShortcut, QProgressBar, QLabel, QSizePolicy, QLayout, QMenu
from PyQt5.QtGui import QColor, QKeySequence, QFont
import re
from utils.param import Param
from key import KeyListenerThread, GlobalKeyListener
from count_down import CountdownWindow
from utils.data_converter import DataConverter
from shortcuts.shortcut_manager import ShortcutManager

class TodoListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.items = []
        self.timer_started = False  # 用于跟踪任务是否已经开始
        self.timer = QTimer()  # 创建 QTimer 对象
        self.__init_ui()
        self.load_items()
        self.time_remaining = Param.remain_time
        self.itemDoubleClicked.connect(self.handle_item_double_clicked)
    def handle_item_double_clicked(self, item):
        print('Item double clicked, its text is:', item.text())
        self.__start_item()
    def __init_ui(self):
        self.__init_menu()
    def __init_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__show_context_menu)
        self.menu = QMenu(self)
        self.__edit_action = self.menu.addAction("编辑(Edit)")
        self.__delete_action = self.menu.addAction("删除(Delete)")
        self.__start_action = self.menu.addAction("开始(Start)")
        self.__delete_action.triggered.connect(self.__delete_item)
        self.__edit_action.triggered.connect(self.__edit_item)
        self.__start_action.triggered.connect(self.__start_item)
    def __show_context_menu(self, pos):
        item = self.itemAt(pos)
        if item:
            self.menu.exec_(self.mapToGlobal(pos))
    def __delete_item(self):
        item = self.currentItem()
        if item:
            self.takeItem(self.row(item))
    def __edit_item(self):
        item = self.currentItem()
        if item:
            # 弹出输入对话框
            text, ok = QInputDialog.getText(self, "编辑", "输入新的内容", text=item.text())
            if ok:
                item.setText(text)
    def start_timer(self):
        self.timer.setInterval(1 * 1 * 1000)  # 时间单位为毫秒
        self.timer.start()  # 启动计时器
    def __start_item(self):
        item = self.currentItem()
        if item:
            # 创建并显示倒计时窗口，设置倒计时时间为20分钟
            self.countdown_window = CountdownWindow(parent=self, item = item)
            self.countdown_window.start_countdown(self.time_remaining)  # 20分钟倒计时
            self.countdown_window.show()
            self.timer_started = True
            print('Task started')
        # 在这里可以添加任务结束时的处理逻辑，比如弹出通知等操作
    def set_item_widget(self, item):
        item.setSizeHint(QSize(Param.item_width, item.get_widget().sizeHint().height()))
        self.setItemWidget(item, item.get_widget())
    def addItem(self, item):
        super().addItem(item)
        self.set_item_widget(item)
    def item_changed(self, item):
        self.save_items()
    def save_items(self):
        self.items = []
        for i in range(self.count()):
            self.items.append(self.item(i))
        from data import Data
        Data.save_items_to_json(self.items)
    def load_items(self):
        from data import Data
        Data.load_items_from_json(list_widget=self)
    def sort_items(self):
        from data import Data
        Data.sort_items(list_widget=self)

class TodoListItem(QListWidgetItem):
    def __init__(self, arg : str, list_widget):
        if isinstance(arg, str):
            print("[TodoListItem] init by text")
            super().__init__(arg)
            self.__init_mems(list_widget)
            self.init_category()
            self.init_widget()
        elif isinstance(arg, dict):
            print("[TodoListItem] init by json")
            super().__init__(arg['text'])
            self.__init_mems(list_widget)
            if arg.get('category'):
                self.category = arg['category']
            # 判断是否有消耗时间的数据
            if arg.get('consume_time'):
                self._consume_time = arg['consume_time']
            self.__init_category(not_by_text=True)
            if arg.get('deadline'):
                self.deadline = QDate.fromString(arg['deadline'], Qt.ISODate) if arg['deadline'] else None
            if arg.get('done'):
                self.checkbox.setChecked(arg['done'])
            if arg.get('donetime'):
                self.donetime = QDate.fromString(arg['donetime'], Qt.ISODate) if arg['donetime'] else None
            if arg.get('createtime'):
                self.createtime = QDate.fromString(arg['createtime'], Qt.ISODate) if arg['createtime'] else None
            self.init_widget()
        elif isinstance(arg, TodoListItem):
            print("[TodoListItem] init by TodoListItem")
            super().__init__()
            self.__init_mems(list_widget)
            self.setText(arg.text())
            self.category = arg.category
            self.deadline = arg.deadline
            self.checkbox = QCheckBox()
            self.checkbox.setChecked(arg.checkbox.isChecked())
            self.init_widget()
    def clone(self):
        return TodoListItem(self, self.list_widget)
    def __init_mems(self, list_widget):
        self.setFont(QFont("Arial", 8))  # 设置默认字体为 Arial，大小为 12
        self._consume_time = 0 #seconds
        self.category = "default"
        self.deadline = None
        self.donetime = None
        self.createtime = None
        self.checkbox = QCheckBox()
        self.widget = QWidget()
        self.priot_label = QLabel()
        self.list_widget = list_widget
    @property
    def consume_time(self):
        return self._consume_time
    @consume_time.setter
    def consume_time(self, value):
        if value < 0:
            raise ValueError("consume_time cannot be negative")
        self._consume_time = value
    def init_category(self):
        self.original_text = self.text()
        self.__init_category()
        self.__init_ddl_by_text()
        self.setText(self.text_fix_by_data)
    def init_widget(self):
        self.__item_background_color()
        self.__done_cb_ui()
        self.__ddl_label_ui()
        self.__item_widget_ui()
    def __init_category(self, not_by_text=False):
        if not not_by_text:
            temp_text = self.text()
            if '#工作' in temp_text or '#work' in temp_text:
                self.category = "work"
            elif '#生活' in temp_text or '#life' in temp_text:
                self.category = "life"
            elif '#学习' in temp_text or '#study' in temp_text:
                self.category = "study" 
            else:
                self.category = "default"

        # 如果包含类别#工作 #生活 #学习 标签，就去掉
        self.text_fix_by_data = re.sub(r'#工作|#work|#生活|#life|#学习|#study', '', self.text())
        self.setText(self.text_fix_by_data)
    def __item_background_color(self):
        if self.category == "work":
            self.setBackground(QColor(144, 238, 144)) # 浅绿色
        elif self.category == "life":
            self.setBackground(QColor(255, 255, 144)) # 浅黄色
        elif self.category == "study":
            self.setBackground(QColor(255, 192, 203)) # 浅红色
        else:
            self.setBackground(Qt.white)
    def __init_ddl_by_text(self):
        self.item_text = self.text()
        self.deadline, self.text_fix_by_data = DataConverter.convert_text_to_date(self.item_text)
    def __ddl_label_ui(self):
        # 根据截止日期的紧急程度设置标签文本和颜色
        if self.deadline is None:
            return
        remaining_days = QDate.currentDate().daysTo(self.deadline)
        if remaining_days < 0:
            priority_color = Param.red  # 红色
        elif remaining_days == 0:
            priority_color = Param.orange  # 橙色
        elif remaining_days == 1:
            priority_color = Param.yellow  # 黄色
        elif remaining_days == 2:
            priority_color = Param.green # 绿色
        else:
            priority_color = Param.blue  # 蓝色

        # 创建标签并设置文本和颜色
        self.priot_label = QLabel(str(remaining_days))
        if not self.checkbox.isChecked():
            self.priot_label.setStyleSheet("background-color: rgb({}, {}, {}, 150); color: white; border-radius: 3px; padding: 2px 5px; font-size: 10px;"
                            .format(priority_color.red(), priority_color.green(), priority_color.blue()))
        else:
            self.priot_label.setStyleSheet("background-color: rgba(128, 128, 128, 100); color: rgba(0, 0, 0, 150); border-radius: 3px; padding: 2px 5px; text-decoration: line-through; font-size: 10px;")

    def __done_cb_ui(self):
        if self.checkbox.isChecked():
            font = self.font()
            font.setStrikeOut(True)
            self.setFont(font)
            self.setData(Qt.UserRole, "done_item")

        self.checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.checkbox.stateChanged.connect(self.__update_item_font_strikeout)
    def __item_widget_ui(self):
        self.widget = QWidget()
        # 设置widget名称
        self.widget.setObjectName("CustomWidget")
        # 将标签添加到水平布局中
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()  # 将标签推到右边
        layout.addWidget(self.priot_label)
        layout.addWidget(self.checkbox)
        # 创建一个 QWidget 来容纳水平布局
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    def get_widget(self):
        if not hasattr(self, 'widget'):
            self.__item_widget_ui()
        return self.widget
    # 在 TodoListItem 类中添加更新字体删除线的方法
    def __update_item_font_strikeout(self, state):
        if state == Qt.Checked:
            font = self.font()
            font.setStrikeOut(True)
            self.setFont(font)
            # 获取当前时间到self.donetime
            self.donetime = QDate.currentDate()
        else:
            font = self.font()
            font.setStrikeOut(False)
            self.setFont(font)
            self.donetime = None
    def get_checkbox(self):
        return self.checkbox
class TDLW(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = None  # 保存鼠标按下时的坐标
        self.init_ui()
    def init_ui(self):
        self.setWindowOpacity(Param.opacity)
        self.__init_mems()
        self.__set_layout()
    def __init_mems(self):
        self.__init_window()
        self.__init_status_bar()
        self.__init_lineedit()
        self.__init_list_widget()
        self.load_btn = QPushButton('Load')
        self.load_btn.clicked.connect(self.list_widget.load_items)
        self.sort_btn = QPushButton('Sort')
        self.sort_btn.clicked.connect(self.list_widget.sort_items)
    def __init_window(self):
        self.setVisible(True)
        self.setWindowTitle('To-Do List')
        self.setGeometry(0, 0, Param.window_width, Param.window_height)
        self.setFixedSize(self.width(), self.height())
        # 获取屏幕的几何信息
        screen = QDesktopWidget().availableGeometry()
        screen_count = QDesktopWidget().screenCount()
        if screen_count > 1:
            first_screen = QDesktopWidget().screenGeometry(0)
            second_screen = QDesktopWidget().screenGeometry(1)
            # 将窗口放在屏幕的右下角
            # self.move(first_screen.width() + second_screen.width() - self.width(), 
            #           first_screen.height() - self.height())
            # 将窗口放在屏幕的左下角
            self.move(first_screen.width(), screen.height() - self.height())
        else:
            self.move(screen.width() - self.width(), screen.height() - self.height())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)  # 设置为无边框模式，并保持最顶层显示
    def __init_status_bar(self):
        self.status_bar = QWidget()
        self.status_bar.setStyleSheet("background-color: gray;")  # 设置背景色为黑色
        self.status_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # 设置大小策略为可扩展的宽度和固定的高度
        # 固定的高度爲30
        self.status_bar.setFixedHeight(Param.status_bar_height)
    def set_status_bar_bg_color_with_delay(self, color, delay_ms=200):
        self.status_bar.setStyleSheet("background-color: {};".format(color))
        QTimer.singleShot(delay_ms, lambda: self.status_bar.setStyleSheet("background-color: gray;"))  # 两秒后恢复为黑色
    def __init_lineedit(self):
        self.input_lineedit = QLineEdit()
        self.input_lineedit.returnPressed.connect(self.add_item)
    def __init_list_widget(self):
        self.list_widget = TodoListWidget()
    def save_items(self):
        self.list_widget.save_items()
        self.set_status_bar_bg_color_with_delay("green")
    def load_items(self):
        self.list_widget.load_items()
        self.set_status_bar_bg_color_with_delay("green")
    def sort_items(self):
        self.list_widget.sort_items()
        self.set_status_bar_bg_color_with_delay("green")
    def __set_layout(self):
        self.lo = QVBoxLayout()
        self.lo.setContentsMargins(0, 0, 0, 0)
        self.func_v_lo = QVBoxLayout()
        self.func_v_lo.addWidget(self.input_lineedit)
        self.btn_h_lo = QHBoxLayout()
        self.btn_h_lo.addWidget(self.load_btn)
        self.btn_h_lo.addWidget(self.sort_btn)
        self.func_v_lo.addLayout(self.btn_h_lo)
        self.func_v_lo.addWidget(self.list_widget)
        self.lo.addWidget(self.status_bar)
        self.lo.addLayout(self.func_v_lo)
        self.setLayout(self.lo)
    def add_item(self):
        text = self.input_lineedit.text()
        if text:
            item = TodoListItem(text, self.list_widget)
            item.createtime = QDate.currentDate()
            self.list_widget.addItem(item)
            self.input_lineedit.clear()
    def delete_item(self):
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    def show_toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
    def closeEvent(self, event):
        app.quit()  # 退出 Qt 事件循环
        event.accept()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    todo_widget = TDLW()
    shortcut_manager = ShortcutManager('config/shortcut_key.json')
    shortcut_manager.load_shortcuts(todo_widget)
    todo_widget.show()
    thread = KeyListenerThread()
    thread.listener.key_pressed.connect(todo_widget.show_toggle)
    thread.start()
    sys.exit(app.exec_())