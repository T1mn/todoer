from PyQt5.QtCore import QObject, QModelIndex, QDate

from model.todo_model import TodoModel, TodoItem
from view.main_window import MainWindow
from utils.data_converter import DataConverter

class AppController(QObject):
    """应用程序的主控制器"""
    def __init__(self, model: TodoModel, view: MainWindow, parent=None):
        super().__init__(parent)
        self._model = model
        self._view = view
        self._connect_signals()

    def _connect_signals(self):
        """连接视图和模型的信号到控制器的槽函数"""
        self._view.add_item_requested.connect(self.add_item)
        self._view.delete_item_requested.connect(self.delete_item)
        self._view.toggle_item_requested.connect(self.toggle_item)
        self._view.sort_items_requested.connect(self.sort_items)
        self._view.save_requested.connect(self._model.save)
        self._view.load_requested.connect(self._model.load)
        # 还可以添加模型信号的连接，例如数据保存成功后在状态栏显示信息

    def add_item(self, text: str):
        """处理添加新项目的请求"""
        # 解析截止日期
        deadline, clean_text = DataConverter.convert_text_to_date(text)
        
        # 解析优先级
        priority, clean_text = DataConverter.convert_text_to_priority(clean_text)
        
        # 解析类别
        category = "default"
        if '#工作' in text or '#work' in text: category = "work"
        elif '#生活' in text or '#life' in text: category = "life"
        elif '#学习' in text or '#study' in text: category = "study"

        # 清理文本（移除所有标识符）
        for category_tag in ['#工作', '#work', '#生活', '#life', '#学习', '#study']:
            clean_text = clean_text.replace(category_tag, '')
        clean_text = clean_text.strip()

        item = TodoItem(text=clean_text, deadline=deadline, category=category, priority=priority)
        self._model.add_item(item)
        # 自动保存数据
        self._model.save()

    def delete_item(self, index: QModelIndex):
        """处理删除项目的请求"""
        if not index.isValid():
            return
        self._model.delete_item(index.row())
        # 自动保存数据
        self._model.save()

    def toggle_item(self, index: QModelIndex):
        """处理切换项目完成状态的请求"""
        if not index.isValid():
            return
        self._model.toggle_item_done(index.row())
        # 自动保存数据
        self._model.save()

    def sort_items(self):
        """处理排序请求并自动保存"""
        self._model.sort_items()
        # 自动保存数据
        self._model.save() 