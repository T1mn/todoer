from PySide6.QtCore import QObject, QModelIndex, QDate, Qt, QTimer
from PySide6.QtWidgets import QMessageBox

from model.todo_model import TodoModel, TodoItem
from model.event_model import EventModel
from view.windows.main_window import MainWindow
from view.dialogs.info_dialog import InfoDialog
from controller.timer_controller import TimerController
from utils.data_converter import DataConverter
from utils.ai_service import GeminiService
from utils.ai_converter import AIConverter
from .ai_parse_handler import AIParseHandler
from .cloud_sync_handler import CloudSyncHandler
from .dialog_manager import DialogManager

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
        
        # 初始化计时器控制器
        self._timer_controller = TimerController()
        
        # 将Timer按钮集成到主界面
        self._integrate_timer_button()
        
        # 初始化 AI 服务
        try:
            self._ai_service = GeminiService()
        except Exception as e:
            print(f"AI 服务初始化失败: {e}")
            self._ai_service = None
        
        self._ai_parse_handler = AIParseHandler(self._model, self._ai_service)
        self._cloud_sync_handler = CloudSyncHandler(self._model)
        self._dialog_manager = DialogManager(self._view)
        self._connect_signals()

    def _integrate_timer_button(self):
        """将Timer按钮集成到主界面布局"""
        try:
            timer_button = self._timer_controller.get_timer_button()
            self._view.add_widget_to_button_layout(timer_button, 1)
            print("✅ Timer按钮已成功集成到主界面")
        except Exception as e:
            print(f"集成Timer按钮失败: {e}")

    def _connect_signals(self):
        """连接视图和模型的信号到控制器的槽函数"""
        self._view.add_item_requested.connect(self.add_item)
        self._view.ai_parse_requested.connect(self._ai_parse_handler.parse_item)
        self._view.delete_item_requested.connect(self.delete_item)
        self._view.toggle_item_requested.connect(self.toggle_item)
        self._view.sort_items_requested.connect(self.sort_items)
        self._view.save_requested.connect(self._model.save)
        
        # 连接云同步信号
        self._view.upload_requested.connect(self._cloud_sync_handler.handle_upload_request)
        self._view.download_requested.connect(self._cloud_sync_handler.handle_download_request)
        
        # 监听视图切换事件
        if hasattr(self._view, 'toggle_buttons'):
            self._view.toggle_buttons.mode_changed.connect(self._on_view_mode_changed)
        
        # 初始连接当前列表视图的信号
        self._connect_current_list_view_signals()

    def _on_view_mode_changed(self, mode: str):
        """处理视图模式切换，重新连接信号"""
        print(f"🔄 [信号调试] 视图模式切换到: {mode}")
        # 重新连接当前活动视图的信号
        self._connect_current_list_view_signals()

    def _connect_current_list_view_signals(self):
        """连接当前活动列表视图的右键菜单信号"""
        try:
            # 断开所有可能的旧连接，避免重复连接
            if hasattr(self._view, 'todo_list_view'):
                try:
                    self._view.todo_list_view.delete_item_requested.disconnect(self.confirm_delete_item)
                    self._view.todo_list_view.show_info_requested.disconnect(self.show_item_info)
                except:
                    pass
            
            if hasattr(self._view, 'time_list_view') and self._view.time_list_view:
                try:
                    self._view.time_list_view.delete_item_requested.disconnect(self.confirm_delete_item)
                    self._view.time_list_view.show_info_requested.disconnect(self.show_item_info)
                except:
                    pass
            
            # 连接当前活动视图的信号
            current_view = self._view.get_list_view()
            if current_view:
                current_view.delete_item_requested.connect(self.confirm_delete_item)
                current_view.show_info_requested.connect(self.show_item_info)
                print(f"✅ [信号调试] 已连接 {current_view.__class__.__name__} 的右键菜单信号")
            else:
                print("❌ [信号调试] 无法获取当前列表视图")
                
        except Exception as e:
            print(f"❌ [信号调试] 连接列表视图信号失败: {e}")

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

            item = TodoItem(description=clean_text, deadline=deadline, category=category, priority=priority)
            self._model.add_item(item)
            # 使用延迟保存
            self._schedule_save()
        except Exception as e:
            print(f"添加项目时出错: {e}")

    

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
        print(f"🗑️ [删除调试] 收到删除请求，索引: {index.row() if index.isValid() else 'INVALID'}")
        
        if not index.isValid():
            print("❌ [删除调试] 索引无效，退出删除操作")
            return
            
        try:
            from model.base_item import BaseItem
            
            item = index.data(Qt.UserRole)
            if not item:
                print("❌ [删除调试] 无法获取项目数据，退出删除操作")
                return
                
            # 统一处理BaseItem类型
            if isinstance(item, BaseItem):
                print(f"📋 [删除调试] 获取{item.item_type}数据: {item.description}")
                
                # 使用统一的确认对话框
                if self._dialog_manager.confirm_delete(item):
                    print("✅ [删除调试] 用户确认删除")
                    QTimer.singleShot(50, lambda: self._execute_delete_item(index, item))
                else:
                    print("ℹ️ [删除调试] 用户取消删除")
            else:
                print(f"❌ [删除调试] 不支持的项目类型: {type(item)}")
                return
                
        except Exception as e:
            print(f"❌ [删除调试] 确认删除时出错: {e}")

    def _execute_delete_item(self, index: QModelIndex, item):
        """执行具体的删除操作"""
        try:
            from model.base_item import BaseItem
            
            if not isinstance(item, BaseItem):
                print(f"❌ [删除调试] 不支持的项目类型: {type(item)}")
                return
                
            current_view = self._view.get_list_view()
            
            if item.item_type == "todo":
                # 删除待办事项
                print("🗑️ [删除调试] 删除待办事项")
                self.delete_item(index)
            elif item.item_type == "record":
                # 删除时间记录
                print("🗑️ [删除调试] 删除时间记录")
                if hasattr(current_view, 'event_model'):
                    row = index.row()
                    if current_view.event_model.delete_event(row):
                        print(f"✅ [删除调试] 时间记录删除成功")
                        # 刷新TimeListView显示
                        if hasattr(current_view, 'time_model'):
                            current_view.time_model.refresh()
                    else:
                        print(f"❌ [删除调试] 时间记录删除失败")
                else:
                    print("❌ [删除调试] 当前视图没有event_model")
            else:
                print(f"❌ [删除调试] 不支持的项目类型: {item.item_type}")
                
        except Exception as e:
            print(f"❌ [删除调试] 执行删除操作时出错: {e}")

    def show_item_info(self, index: QModelIndex):
        if not index.isValid():
            return
        item = index.data(Qt.UserRole)
        if not item:
            return
        self._dialog_manager.show_item_info(item)

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