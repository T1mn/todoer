"""
待办事项数据模型模块

定义待办事项的数据结构和管理逻辑，继承自BaseItem，
严格遵循数据与视图分离的原则。
"""

import json
from datetime import datetime
from enum import Enum
from typing import Dict, Any

from PySide6.QtCore import QModelIndex, Qt, QDate
from dataclasses import dataclass, field, asdict

from .base_item import BaseItem
from .base_model import BaseModel



class Priority(Enum):
    """任务重要程度枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

    @property
    def display_name(self) -> str:
        """获取显示名称"""
        display_map = {
            Priority.LOW: "低",
            Priority.MEDIUM: "中等", 
            Priority.HIGH: "高",
            Priority.URGENT: "紧急"
        }
        return display_map.get(self, "中等")

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def from_string(cls, value: str) -> 'Priority':
        """从字符串创建Priority对象"""
        try:
            return cls[value.upper()]
        except KeyError:
            return cls.MEDIUM

@dataclass
class TodoItem(BaseItem):
    """待办事项数据类
    
    继承自BaseItem，包含待办事项特有的属性和逻辑。
    严格遵循数据模型职责，不包含任何界面显示逻辑。
    
    Attributes:
        done: 完成状态
        priority: 优先级
        deadline: 截止日期
        donetime: 完成时间
        consume_time: 预估消耗时间（分钟）
    """
    done: bool = False
    priority: Priority = Priority.MEDIUM
    deadline: QDate = None
    donetime: QDate = None
    consume_time: int = 0

    def __post_init__(self) -> None:
        """初始化后处理，设置类型标识和数据验证"""
        self.item_type = "todo"
        self._item_type_set = True
        super().__post_init__()
        
        # 数据验证和转换
        if isinstance(self.priority, str):
            self.priority = Priority.from_string(self.priority)
        elif isinstance(self.priority, int):
            try:
                self.priority = Priority(self.priority)
            except ValueError:
                self.priority = Priority.MEDIUM

    @property
    def text(self) -> str:
        """向后兼容性接口 - 返回描述文本"""
        return self.description

    @text.setter  
    def text(self, value: str) -> None:
        """向后兼容性接口 - 设置描述文本"""
        self.description = value

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典，包含所有待办事项字段"""
        base_dict = super().to_dict()
        base_dict.update({
            "text": self.description,  # 保持向后兼容
            "done": self.done,
            "priority": self.priority.value,
            "deadline": self.deadline.toString() if self.deadline else None,
            "createtime": self.created_time.strftime('%Y-%m-%d'),  # 兼容旧格式
            "donetime": self.donetime.toString() if self.donetime else None,
            "consume_time": self.consume_time
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoItem':
        """从字典反序列化待办事项对象
        
        Args:
            data: 包含待办事项数据的字典
            
        Returns:
            反序列化后的TodoItem实例
        """
        # 处理时间字段的兼容性
        created_time = data.get("created_time")
        if created_time:
            try:
                created_time = datetime.fromisoformat(created_time)
            except ValueError:
                created_time = datetime.now()
        else:
            # 兼容旧格式的createtime字段
            createtime_str = data.get("createtime")
            if createtime_str:
                try:
                    created_time = datetime.strptime(createtime_str, '%Y-%m-%d')
                except ValueError:
                    created_time = datetime.now()
            else:
                created_time = datetime.now()
        
        return cls(
            description=data.get("text", data.get("description", "")),
            category=data.get("category", "default"),
            created_time=created_time,
            done=data.get("done", False),
            priority=Priority(data.get("priority", Priority.MEDIUM.value)),
            deadline=QDate.fromString(data["deadline"]) if data.get("deadline") else None,
            donetime=QDate.fromString(data["donetime"]) if data.get("donetime") else None,
            consume_time=data.get("consume_time", 0)
        )

class TodoModel(BaseModel):
    """待办事项的核心模型"""
    def __init__(self, user_id, key_path):
        super().__init__(user_id, key_path, 'todo_events.json', 'todo_events')
        print(f"📝 [TodoModel] 初始化完成，加载了 {len(self._items)} 个待办事项")
        for i, item in enumerate(self._items):
            print(f"  {i+1}. {item.text} (done: {item.done})")

    def _dict_to_item(self, data: dict) -> TodoItem:
        """将字典转换为 TodoItem 对象"""
        return TodoItem.from_dict(data)

    def _item_to_dict(self, item: TodoItem) -> dict:
        """将 TodoItem 转换为字典"""
        return item.to_dict()

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