from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QListWidgetItem, QMessageBox, QPushButton

class CountdownWindow(QWidget):
    def __init__(self, parent = None, item : QListWidgetItem = None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setWindowTitle('倒计时')
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 设置为无边框模式，并保持最顶层显示
        if parent:
            self.setWindowFlags(parent.windowFlags())
            self.setFixedHeight(parent.height())
            self.setFixedWidth(parent.width())
        else:
            self.setFixedSize(200, 100)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)

        if item:
            self.item = item
            self.task_label = QLabel(item.text(), self)
        else:
            self.task_label = QLabel('No task', self)

        self.label = QLabel('00:00', self)
        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.clicked.connect(self.close)

        self.consume_time = 0
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.task_label)
        layout.addWidget(self.cancel_btn)
        self.setLayout(layout)

    def start_countdown(self, duration):
        self.remaining_time = duration
        self.update_display()
        self.timer.start(1000)

    def update_display(self):
        self.consume_time += 1
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_text = '{:02d}:{:02d}'.format(minutes, seconds)
        self.label.setText(time_text)
    

    def on_timeout(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.timer.stop()
            self.close()
            # show a message box
            msg_box = QMessageBox()
            msg_box.setText('Time is up! Please take a break.')
            msg_box.exec()
        else:
            self.update_display()

    def closeEvent(self, event):
        self.timer.stop()
        if self.item:
            self.item.consume_time = self.item.consume_time + self.consume_time
            print('consume time:', self.item.consume_time)
        event.accept()
