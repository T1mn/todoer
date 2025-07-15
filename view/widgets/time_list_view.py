from view.widgets.base_list_view import BaseListView
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
from model.event_model import EventRecord
from datetime import datetime


class TimeListModel(QAbstractListModel):
    """时间记录列表的数据模型"""
    
    def __init__(self, event_model, parent=None):
        super().__init__(parent)
        self.event_model = event_model
        self._events = []
        self._load_events()
    
    def _load_events(self):
        """从EventModel加载事件数据"""
        if hasattr(self.event_model, '_items'):
            self._events = list(self.event_model._items)
            # 按时间倒序排列
            self._events.sort(key=lambda x: x.end_time, reverse=True)
    
    def rowCount(self, parent=QModelIndex()):
        """返回行数"""
        return len(self._events)
    
    def data(self, index, role=Qt.DisplayRole):
        """返回数据"""
        if not index.isValid() or not 0 <= index.row() < len(self._events):
            return None
        
        event = self._events[index.row()]
        
        if role == Qt.DisplayRole:
            # 格式化显示文本
            duration_minutes = event.duration_seconds // 60
            time_str = event.end_time.strftime("%H:%M")
            return f"{time_str} | {event.category} | {duration_minutes}分钟\n{event.event_description}"
        elif role == Qt.UserRole:
            return event
        
        return None
    
    def refresh(self):
        """刷新数据"""
        self.beginResetModel()
        self._load_events()
        self.endResetModel()


class TimeListView(BaseListView):
    """
    时间记录列表视图
    显示已完成的时钟倒计时项目
    """
    
    def __init__(self, event_model, parent=None):
        super().__init__(parent)
        self.event_model = event_model
        self._setup_model()
        self._connect_event_model_signals()
    
    def _setup_model(self):
        """设置数据模型"""
        self.time_model = TimeListModel(self.event_model)
        self.setModel(self.time_model)
    
    def _connect_event_model_signals(self):
        """连接事件模型信号"""
        if hasattr(self.event_model, 'event_saved'):
            self.event_model.event_saved.connect(self._on_event_saved)
    
    def _on_event_saved(self, description):
        """当新事件保存时刷新列表"""
        self.time_model.refresh()
    
    def get_display_name(self) -> str:
        """返回列表类型名称"""
        return "时间记录"
    
    def get_empty_message(self) -> str:
        """返回空列表时的提示信息"""
        return "暂无时间记录\n完成番茄钟后会自动记录"
    
    def handle_empty_state(self):
        """处理空列表状态显示"""
        # 可以在这里添加空状态的特殊处理
        pass
    
    def refresh_data(self):
        """刷新数据"""
        self.time_model.refresh() 