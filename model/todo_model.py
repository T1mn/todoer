import json
from enum import Enum
from PySide6.QtCore import QModelIndex, Qt, QDate
from dataclasses import dataclass, field, asdict
from .base_model import BaseModel



class Priority(Enum):
    """任务重要程度枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_string(cls, value: str):
        """从字符串创建Priority对象"""
        try:
            return cls[value.upper()]
        except KeyError:
            return cls.MEDIUM

@dataclass
class TodoItem:
    """待办事项的数据类"""
    text: str
    done: bool = False
    category: str = "default"
    priority: Priority = Priority.MEDIUM
    deadline: QDate = None
    createtime: QDate = field(default_factory=QDate.currentDate)
    donetime: QDate = None
    consume_time: int = 0

    def __post_init__(self):
        """数据验证和处理"""
        if isinstance(self.priority, str):
            self.priority = Priority.from_string(self.priority)
        if isinstance(self.priority, int):
            try:
                self.priority = Priority(self.priority)
            except ValueError:
                self.priority = Priority.MEDIUM

class TodoModel(BaseModel):
    """待办事项的核心模型"""
    def __init__(self, user_id, key_path):
        super().__init__(user_id, key_path, 'todo_events.json', 'todo_events')
        print(f"📝 [TodoModel] 初始化完成，加载了 {len(self._items)} 个待办事项")
        for i, item in enumerate(self._items):
            print(f"  {i+1}. {item.text} (done: {item.done})")

    def _dict_to_item(self, data: dict) -> TodoItem:
        """将字典转换为 TodoItem 对象"""
        # 处理日期字段
        for key in ['deadline', 'createtime', 'donetime']:
            if data.get(key):
                data[key] = QDate.fromString(data[key], Qt.ISODate)
        
        # 处理优先级字段
        if 'priority' in data:
            if isinstance(data['priority'], int):
                try:
                    data['priority'] = Priority(data['priority'])
                except ValueError:
                    data['priority'] = Priority.MEDIUM
            elif isinstance(data['priority'], str):
                data['priority'] = Priority.from_string(data['priority'])
        
        return TodoItem(**data)

    def _item_to_dict(self, item: TodoItem) -> dict:
        """将 TodoItem 转换为字典"""
        data = asdict(item)
        # 处理日期和枚举序列化
        for key in ['deadline', 'createtime', 'donetime']:
            if data.get(key) and isinstance(data[key], QDate):
                data[key] = data[key].toString(Qt.ISODate)
        if isinstance(data.get('priority'), Priority):
            data['priority'] = data['priority'].value
        return data

    def add_item(self, item: TodoItem):
        """在列表末尾添加一个新项目"""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(item)
        self.endInsertRows()

    def delete_item(self, row: int):
        """删除指定行的项目"""
        if not 0 <= row < len(self._items):
            return False
        
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._items[row]
        self.endRemoveRows()
        return True

    def toggle_item_done(self, row: int):
        """切换指定行项目的完成状态"""
        if not 0 <= row < self.rowCount():
            return
        
        item = self._items[row]
        item.done = not item.done
        
        if item.done:
            item.donetime = QDate.currentDate()
        else:
            item.donetime = None
        
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.UserRole])

    def sort_items(self):
        """根据完成状态、优先级和截止日期对项目进行排序"""
        self.beginResetModel()
        self._items.sort(key=lambda item: (
            item.done,
            -item.priority.value,
            item.deadline or QDate(9999, 12, 31)
        ))
        self.endResetModel() 