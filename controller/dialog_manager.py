"""
对话框管理器模块

提供统一的对话框管理接口，利用多态性处理不同类型的BaseItem，
严格遵循单一职责原则。
"""

from PySide6.QtWidgets import QMessageBox

from model.base_item import BaseItem
from view.windows.main_window import MainWindow
from view.dialogs.info_dialog import InfoDialog


class DialogManager:
    """对话框管理器 - 统一处理各种BaseItem类型的对话框"""

    def __init__(self, parent: MainWindow):
        self._parent = parent

    def show_item_info(self, item: BaseItem) -> None:
        """统一的项目信息显示 - 利用多态性和InfoDialog的智能适配
        
        Args:
            item: 任何BaseItem的子类实例
        """
        try:
            dialog = InfoDialog(item, self._parent)
            dialog.exec_()
        except Exception as e:
            print(f"❌ [对话框] 显示项目信息失败: {e}")
            # 作为备选方案，显示简单的消息框
            self._show_fallback_info(item)

    def _show_fallback_info(self, item: BaseItem) -> None:
        """备选信息显示方案"""
        msg_box = QMessageBox(self._parent)
        msg_box.setWindowTitle(f"{item.item_type.title()} 信息")
        msg_box.setText(f"描述: {item.description}\n类别: {item.category}")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def confirm_delete(self, item: BaseItem) -> bool:
        """统一的删除确认对话框
        
        Args:
            item: 任何BaseItem的子类实例
            
        Returns:
            用户是否确认删除
        """
        type_names = {"todo": "任务", "record": "记录"}
        type_name = type_names.get(item.item_type, "项目")
        
        msg_box = QMessageBox(self._parent)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f"确定要删除{type_name}吗？\n\n内容：{item.description}")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        result = msg_box.exec_()
        return result == QMessageBox.Yes
