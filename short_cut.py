import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QShortcut
from PyQt5.QtGui import QKeySequence

class ShortcutHandler:
    def __init__(self, shortcut_key, callback):
        self.shortcut_key = shortcut_key
        self.callback = callback

    def set_shortcut(self, window):
        self.shortcut = QShortcut(QKeySequence(self.shortcut_key), window)
        self.shortcut.activated.connect(self.callback)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Shortcut Example')
        # 创建一个动作
        self.action = QAction('Exit', self)
        self.action.setShortcut(QKeySequence.Quit)  # 设置全局快捷键为 Ctrl+Q
        self.action.triggered.connect(self.close)  # 关联关闭窗口的槽函数

        # 在菜单栏中添加一个动作
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('&File')
        self.file_menu.addAction(self.action)

def open_file():
    print('Opening file...')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    # 创建 ShortcutHandler 实例，并将外部函数 open_file 和快捷键 'Ctrl+O' 传递给它
    shortcut_handler = ShortcutHandler('Ctrl+O', open_file)
    shortcut_handler.set_shortcut(window)

    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
