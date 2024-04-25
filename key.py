from pynput import keyboard
from PyQt5.QtCore import QObject, QThread, pyqtSignal
class GlobalKeyListener(QObject):
    key_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.alt_pressed = False

    def on_press(self, key):
        if key == keyboard.Key.alt:
            self.alt_pressed = True
        elif self.alt_pressed and key == keyboard.KeyCode.from_char('t'):
            self.key_pressed.emit()
            self.alt_pressed = False
        else:
            self.alt_pressed = False

    def on_release(self, key):
        if key == keyboard.Key.alt:
            self.alt_pressed = False

class KeyListenerThread(QThread):
    def __init__(self):
        super().__init__()
        self.listener = GlobalKeyListener()

    def run(self):
        with keyboard.Listener(on_press=self.listener.on_press, on_release=self.listener.on_release) as listener:
            listener.join()
