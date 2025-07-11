from PyQt5.QtCore import QObject, QModelIndex, QDate, Qt, QTimer
from PyQt5.QtWidgets import QMessageBox

from model.todo_model import TodoModel, TodoItem
from view.main_window import MainWindow
from view.info_dialog import InfoDialog
from utils.data_converter import DataConverter
from utils.ai_service import GeminiService
from utils.ai_converter import AIConverter

class AppController(QObject):
    """应用程序的主控制器"""
    def __init__(self, model: TodoModel, view: MainWindow, parent=None):
        super().__init__(parent)
        self._model = model
        self._view = view
        
        # 初始化延迟保存定时器
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._delayed_save)
        
        # 初始化 AI 服务
        try:
            self._ai_service = GeminiService()
        except Exception as e:
            print(f"AI 服务初始化失败: {e}")
            self._ai_service = None
        
        self._connect_signals()

    def _connect_signals(self):
        """连接视图和模型的信号到控制器的槽函数"""
        self._view.add_item_requested.connect(self.add_item)
        self._view.ai_parse_requested.connect(self.ai_parse_item)
        self._view.delete_item_requested.connect(self.delete_item)
        self._view.toggle_item_requested.connect(self.toggle_item)
        self._view.sort_items_requested.connect(self.sort_items)
        self._view.save_requested.connect(self._model.save)
        self._view.load_requested.connect(self._model.load)
        
        # 连接列表视图的新信号
        try:
            list_view = self._view.get_list_view()
            list_view.delete_item_requested.connect(self.confirm_delete_item)
            list_view.show_info_requested.connect(self.show_item_info)
        except Exception as e:
            print(f"警告：信号连接失败: {e}")

    def _delayed_save(self):
        """延迟保存数据，避免在模型更新期间立即保存"""
        try:
            self._model.save()
        except Exception as e:
            print(f"保存数据时出错: {e}")

    def _schedule_save(self):
        """安排延迟保存，避免频繁保存操作"""
        self._save_timer.stop()
        self._save_timer.start(500)  # 500ms后保存

    def add_item(self, text: str):
        """处理添加新项目的请求"""
        try:
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
            # 使用延迟保存
            self._schedule_save()
        except Exception as e:
            print(f"添加项目时出错: {e}")

    def ai_parse_item(self, text: str):
        """处理 AI 解析项目的请求"""
        if not self._ai_service or not self._ai_service.is_available():
            # AI 服务不可用，回退到普通解析
            self.add_item(text)
            return
        
        try:
            # 使用 AI 服务解析文本
            ai_result = self._ai_service.parse_todo_text(text)
            
            # 转换为 TodoItem
            todo_item = AIConverter.convert_ai_to_todo_item(ai_result)
            
            # 添加到模型
            self._model.add_item(todo_item)
            
            # 使用延迟保存
            self._schedule_save()
            
        except Exception as e:
            print(f"AI 解析失败，回退到普通解析: {e}")
            # 回退到普通解析
            self.add_item(text)

    def delete_item(self, index: QModelIndex):
        """处理删除项目的请求（内部方法，不带确认）"""
        if not index.isValid():
            return
            
        try:
            row = index.row()
            if 0 <= row < self._model.rowCount():
                self._model.delete_item(row)
                # 使用延迟保存，避免在模型操作期间立即保存
                self._schedule_save()
        except Exception as e:
            print(f"删除项目时出错: {e}")

    def confirm_delete_item(self, index: QModelIndex):
        """确认删除项目（带确认对话框）"""
        if not index.isValid():
            return
            
        try:
            item = index.data(Qt.UserRole)
            if not item:
                return
                
            # 创建确认对话框
            msg_box = QMessageBox(self._view)
            msg_box.setWindowTitle("确认删除")
            msg_box.setText(f"确定要删除任务吗？\n\n任务内容：{item.text}")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            
            # 应用圆角样式
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2E2E2E;
                    color: #E0E0E0;
                }
                QMessageBox QPushButton {
                    background-color: #4A4A4A;
                    color: #E0E0E0;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    min-width: 60px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #555555;
                }
            """)
            
            # 使用异步方式处理确认结果，避免阻塞
            result = msg_box.exec_()
            if result == QMessageBox.Yes:
                # 延迟执行删除操作，让确认对话框完全关闭
                QTimer.singleShot(50, lambda: self.delete_item(index))
                
        except Exception as e:
            print(f"确认删除时出错: {e}")

    def show_item_info(self, index: QModelIndex):
        """显示项目详细信息"""
        if not index.isValid():
            return
            
        try:
            item = index.data(Qt.UserRole)
            if not item:
                return
                
            # 创建并显示信息对话框
            dialog = InfoDialog(item, self._view)
            dialog.exec_()
        except Exception as e:
            print(f"显示项目信息时出错: {e}")

    def toggle_item(self, index: QModelIndex):
        """处理切换项目完成状态的请求"""
        if not index.isValid():
            return
            
        try:
            self._model.toggle_item_done(index.row())
            # 使用延迟保存
            self._schedule_save()
        except Exception as e:
            print(f"切换项目状态时出错: {e}")

    def sort_items(self):
        """处理排序请求并自动保存"""
        try:
            self._model.sort_items()
            # 使用延迟保存
            self._schedule_save()
        except Exception as e:
            print(f"排序项目时出错: {e}") 