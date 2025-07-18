"""
时间记录数据模型模块

定义时间记录的数据结构和管理逻辑，继承自BaseItem，
严格遵循数据与视图分离的原则。
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

from PySide6.QtCore import Signal

from .base_item import BaseItem
from .base_model import BaseModel

@dataclass
class RecordItem(BaseItem):
    """时间记录数据类
    
    继承自BaseItem，包含时间记录特有的属性和逻辑。
    严格遵循数据模型职责，不包含任何界面显示逻辑。
    
    Attributes:
        start_time: 开始时间
        end_time: 结束时间  
        duration_seconds: 持续时间（秒）
        event_type: 事件类型
    """
    start_time: datetime = None
    end_time: datetime = None
    duration_seconds: int = 0
    event_type: str = "pomodoro"

    def __post_init__(self) -> None:
        """初始化后处理，设置类型标识"""
        self.item_type = "record"
        self._item_type_set = True
        super().__post_init__()

    @property
    def event_description(self) -> str:
        """向后兼容性接口 - 返回描述文本"""
        return self.description

    @event_description.setter
    def event_description(self, value: str) -> None:
        """向后兼容性接口 - 设置描述文本"""
        self.description = value

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典，包含所有时间记录字段"""
        base_dict = super().to_dict()
        base_dict.update({
            "event_description": self.description,  # 保持向后兼容
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "event_type": self.event_type
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecordItem':
        """从字典反序列化时间记录对象
        
        Args:
            data: 包含时间记录数据的字典
            
        Returns:
            反序列化后的RecordItem实例
        """
        # 处理时间字段
        created_time = data.get("created_time")
        if created_time:
            try:
                created_time = datetime.fromisoformat(created_time)
            except ValueError:
                created_time = datetime.now()
        else:
            created_time = datetime.now()

        start_time = None
        if data.get("start_time"):
            try:
                start_time = datetime.fromisoformat(data["start_time"])
            except ValueError:
                start_time = None

        end_time = None
        if data.get("end_time"):
            try:
                end_time = datetime.fromisoformat(data["end_time"])
            except ValueError:
                end_time = None

        return cls(
            description=data.get("event_description", data.get("description", "")),
            category=data.get("category", "default"),
            created_time=created_time,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=data.get("duration_seconds", 0),
            event_type=data.get("event_type", "pomodoro")
        )


class EventModel(BaseModel):
    event_saved = Signal(str)

    def __init__(self, user_id: str, key_path: str):
        self.current_session_start: Optional[datetime] = None
        super().__init__(user_id, key_path, 'event_records.json', 'event_records')

    def get_default_data_structure(self) -> dict:
        return {"events": []}

    def _dict_to_item(self, data: dict) -> RecordItem:
        return RecordItem.from_dict(data)

    def _item_to_dict(self, item: RecordItem) -> dict:
        return item.to_dict()
    
    def save(self):
        """重写save方法，使用events而不是items"""
        with open(self._data_file_path, 'w', encoding='utf-8') as f:
            data = {'events': [self._item_to_dict(item) for item in self._items]}
            json.dump(data, f, ensure_ascii=False, indent=2)

    def start_session(self):
        self.current_session_start = datetime.now()

    def end_session(self, event_description: str, category: str = "default") -> RecordItem:
        if not self.current_session_start:
            return None
        end_time = datetime.now()
        duration = int((end_time - self.current_session_start).total_seconds())
        event = RecordItem(
            description=event_description,
            start_time=self.current_session_start,
            end_time=end_time,
            duration_seconds=duration,
            category=category
        )
        # 添加到内部数据结构
        self._items.append(event)
        # 保存到文件
        self.save()
        self.event_saved.emit(event_description)
        self.current_session_start = None
        return event

    def get_today_summary(self) -> dict:
        today = datetime.now().date()
        today_events = [event for event in self._items if event.start_time.date() == today]
        total_duration = sum(event.duration_seconds for event in today_events)
        category_stats = {}
        for event in today_events:
            category = event.category
            if category not in category_stats:
                category_stats[category] = {"count": 0, "total_duration": 0, "events": []}
            category_stats[category]["count"] += 1
            category_stats[category]["total_duration"] += event.duration_seconds
            category_stats[category]["events"].append(event.event_description)
        return {
            "total_events": len(today_events),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": f"{total_duration // 3600}h {total_duration % 3600 // 60}m",
            "categories": category_stats,
        }

    def delete_event(self, row: int):
        """删除指定行的事件记录"""
        if not 0 <= row < len(self._items):
            return False
        
        self.beginRemoveRows(self.createIndex(row, 0).parent(), row, row)
        del self._items[row]
        self.endRemoveRows()
        
        # 保存到文件
        self.save()
        return True