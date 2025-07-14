from PySide6.QtWidgets import QMessageBox
from model.todo_model import TodoItem
from view.windows.main_window import MainWindow
from view.dialogs.info_dialog import InfoDialog

class DialogManager:
    def __init__(self, parent: MainWindow):
        self._parent = parent

    def show_item_info(self, item: TodoItem):
        """显示项目详细信息对话框"""
        dialog = InfoDialog(item, self._parent)
        dialog.exec_()

    def confirm_delete(self, item: TodoItem) -> bool:
        """显示删除确认对话框并返回用户的选择"""
        msg_box = QMessageBox(self._parent)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f"确定要删除任务吗？\n\n任务内容：{item.text}")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        result = msg_box.exec_()
        return result == QMessageBox.Yes
