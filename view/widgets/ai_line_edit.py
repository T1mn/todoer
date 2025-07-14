from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QKeyEvent

class AILineEdit(QLineEdit):
    """支持 AI 解析的自定义 QLineEdit"""
    ai_parse_requested = Signal(str)
    
    def keyPressEvent(self, event: QKeyEvent):
        """重写键盘事件处理，支持 Shift+Enter"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._handle_ai_parse()
                return
            
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def _handle_ai_parse(self):
        """处理AI解析请求"""
        text = self.text()
        if text:
            self.ai_parse_requested.emit(text)
            self.clear()
