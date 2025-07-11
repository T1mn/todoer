import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal

# 导入日志管理器  
try:
    from utils.logger import module_logger
    def log_event(action: str, details: str):
        module_logger.log_timer_event(action, details)
except ImportError:
    def log_event(action: str, details: str):
        print(f"[EVENT-{action}] {details}")

@dataclass
class EventRecord:
    """事件记录数据类"""
    event_description: str          # 事件描述
    start_time: datetime           # 开始时间
    end_time: datetime            # 结束时间  
    duration_seconds: int         # 持续时长(秒)
    event_type: str = "pomodoro"  # 事件类型(番茄时间/休息等)
    category: str = "default"     # 事件类别
    
    def to_dict(self) -> dict:
        """转换为字典格式用于JSON序列化"""
        return {
            "event_description": self.event_description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "event_type": self.event_type,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EventRecord':
        """从字典创建EventRecord对象"""
        return cls(
            event_description=data["event_description"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            duration_seconds=data["duration_seconds"],
            event_type=data.get("event_type", "pomodoro"),
            category=data.get("category", "default")
        )

class EventModel(QObject):
    """事件记录模型"""
    
    # 信号定义
    event_saved = pyqtSignal(str)  # 事件保存完成信号
    
    def __init__(self, data_file="event_records.json"):
        super().__init__()
        self.data_file = data_file
        self.events: List[EventRecord] = []
        self.current_session_start: Optional[datetime] = None
        self.load_events()
    
    def start_session(self):
        """开始一个新的事件会话"""
        self.current_session_start = datetime.now()
        log_event("session_start", f"Event session started at {self.current_session_start.strftime('%H:%M:%S')}")
    
    def end_session(self, event_description: str, category: str = "default") -> EventRecord:
        """结束当前事件会话并记录"""
        if not self.current_session_start:
            log_event("session_end_warning", "No active event session to end.")
            return None
        
        end_time = datetime.now()
        duration = int((end_time - self.current_session_start).total_seconds())
        
        event = EventRecord(
            event_description=event_description,
            start_time=self.current_session_start,
            end_time=end_time,
            duration_seconds=duration,
            category=category
        )
        
        self.events.append(event)
        self.save_events()
        
        log_event("event_recorded", f"Event recorded: {event_description} ({duration//60}分{duration%60}秒)")
        self.event_saved.emit(event_description)
        
        # 重置会话状态
        self.current_session_start = None
        return event
    
    def get_today_events(self) -> List[EventRecord]:
        """获取今天的事件记录"""
        today = datetime.now().date()
        return [event for event in self.events 
                if event.start_time.date() == today]
    
    def get_events_by_date(self, target_date) -> List[EventRecord]:
        """获取指定日期的事件记录"""
        return [event for event in self.events 
                if event.start_time.date() == target_date]
    
    def get_daily_summary(self) -> dict:
        """获取今日统计摘要"""
        today_events = self.get_today_events()
        total_duration = sum(event.duration_seconds for event in today_events)
        
        # 按类别统计
        category_stats = {}
        for event in today_events:
            category = event.category
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "total_duration": 0,
                    "events": []
                }
            category_stats[category]["count"] += 1
            category_stats[category]["total_duration"] += event.duration_seconds
            category_stats[category]["events"].append(event.event_description)
        
        return {
            "total_events": len(today_events),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": f"{total_duration//3600}小时{(total_duration%3600)//60}分钟",
            "categories": category_stats,
            "events": today_events
        }
    
    def save_events(self):
        """保存事件记录到本地文件"""
        try:
            # 确保config目录存在
            config_dir = "config"
            os.makedirs(config_dir, exist_ok=True)
            
            # 转换为可序列化的格式
            events_data = [event.to_dict() for event in self.events]
            
            file_path = os.path.join(config_dir, self.data_file)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, ensure_ascii=False, indent=2)
            
            log_event("events_saved", f"Event records saved: {len(self.events)} records")
        except Exception as e:
            log_event("save_events_failed", f"Failed to save event records: {e}")
    
    def load_events(self):
        """从本地文件加载事件记录"""
        try:
            file_path = os.path.join("config", self.data_file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                
                self.events = [EventRecord.from_dict(data) for data in events_data]
                log_event("events_loaded", f"Event records loaded: {len(self.events)} records")
            else:
                log_event("events_loaded", "First time use, creating new event records")
        except Exception as e:
            log_event("load_events_failed", f"Failed to load event records: {e}")
            self.events = []
    
    def delete_event(self, index: int) -> bool:
        """删除指定索引的事件记录"""
        try:
            if 0 <= index < len(self.events):
                deleted_event = self.events.pop(index)
                self.save_events()
                log_event("event_deleted", f"Event deleted: {deleted_event.event_description}")
                return True
        except Exception as e:
            log_event("delete_event_failed", f"Failed to delete event: {e}")
        return False 