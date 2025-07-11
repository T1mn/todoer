import json
from enum import Enum
from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QDate
from dataclasses import dataclass, field, asdict

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
            return cls.MEDIUM  # 默认返回中等重要

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

class TodoModel(QAbstractListModel):
    """待办事项的核心模型"""
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._items = []
        self._file_path = file_path

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """返回模型中的行数"""
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """根据索引和角色返回数据"""
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return None

        item = self._items[index.row()]
        if role == Qt.DisplayRole:
            return item.text
        elif role == Qt.UserRole:  # 使用用户角色返回整个对象
            return item
        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        """设置指定索引的数据"""
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        if 0 <= row < self.rowCount():
            self._items[row] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.UserRole])
            return True
        return False

    def load(self):
        """从 JSON 文件加载数据"""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        
        self.beginResetModel()
        self._items = [self._dict_to_item(item_data) for item_data in data]
        self.endResetModel()

    def save(self):
        """将数据保存到 JSON 文件"""
        with open(self._file_path, 'w', encoding='utf-8') as f:
            data = [asdict(item) for item in self._items]
            json.dump(data, f, ensure_ascii=False, indent=4, default=self._json_serializer)

    def _json_serializer(self, obj):
        """处理 QDate 和 Priority 对象的 JSON 序列化"""
        if isinstance(obj, QDate):
            return obj.toString(Qt.ISODate)
        elif isinstance(obj, Priority):
            return obj.value  # 保存为整数值
        raise TypeError(f"Type {type(obj)} not serializable")

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

    def add_item(self, item: TodoItem):
        """在列表末尾添加一个新项目"""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(item)
        self.endInsertRows()

    def delete_item(self, row: int):
        """删除指定行的项目"""
        if not 0 <= row < self.rowCount():
            return
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._items[row]
        self.endRemoveRows()

    def toggle_item_done(self, row: int):
        """切换指定行项目的完成状态"""
        if not 0 <= row < self.rowCount():
            return
        
        item = self._items[row]
        item.done = not item.done
        
        # 设置完成时间
        if item.done:
            item.donetime = QDate.currentDate()
        else:
            item.donetime = None
        
        # 通知视图数据已更改
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.UserRole])

    def sort_items(self):
        """根据完成状态、优先级和截止日期对项目进行排序"""
        self.beginResetModel()
        self._items.sort(key=lambda item: (
            item.done,  # 未完成的排在前面
            -item.priority.value,  # 优先级高的排在前面（负号用于降序）
            item.deadline or QDate(9999, 12, 31)  # 截止日期近的排在前面
        ))
        self.endResetModel()

    def sort_by_priority(self):
        """按优先级排序"""
        self.beginResetModel()
        self._items.sort(key=lambda item: (-item.priority.value, item.done))
        self.endResetModel()

    def sort_by_deadline(self):
        """按截止日期排序"""
        self.beginResetModel()
        self._items.sort(key=lambda item: (
            item.done,
            item.deadline or QDate(9999, 12, 31)
        ))
        self.endResetModel()

    def sort_by_category(self):
        """按类别排序"""
        self.beginResetModel()
        self._items.sort(key=lambda item: (item.done, item.category, -item.priority.value))
        self.endResetModel()

    def filter_by_category(self, category: str):
        """按类别筛选（返回筛选后的项目列表，不修改原数据）"""
        return [item for item in self._items if item.category == category]

    def filter_by_priority(self, priority: Priority):
        """按优先级筛选（返回筛选后的项目列表，不修改原数据）"""
        return [item for item in self._items if item.priority == priority] 