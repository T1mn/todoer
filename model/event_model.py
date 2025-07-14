from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from PySide6.QtCore import Signal
from .base_model import BaseModel

@dataclass
class EventRecord:
    event_description: str
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    event_type: str = "pomodoro"
    category: str = "default"

    def to_dict(self) -> dict:
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
        return cls(
            event_description=data["event_description"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            duration_seconds=data["duration_seconds"],
            event_type=data.get("event_type", "pomodoro"),
            category=data.get("category", "default")
        )

class EventModel(BaseModel):
    event_saved = Signal(str)

    def __init__(self, user_id: str, key_path: str):
        self.current_session_start: Optional[datetime] = None
        super().__init__(user_id, key_path, 'event_records.json', 'event_records')

    def get_default_data_structure(self) -> dict:
        return {"events": []}

    def _dict_to_item(self, data: dict) -> EventRecord:
        return EventRecord.from_dict(data)

    def _item_to_dict(self, item: EventRecord) -> dict:
        return item.to_dict()

    def start_session(self):
        self.current_session_start = datetime.now()

    def end_session(self, event_description: str, category: str = "default") -> EventRecord:
        if not self.current_session_start:
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
        self.data['events'].append(self._item_to_dict(event))
        self.save_to_local()
        self.event_saved.emit(event_description)
        self.current_session_start = None
        return event

    def get_today_summary(self) -> dict:
        today = datetime.now().date()
        today_events = [self._dict_to_item(e) for e in self.data['events'] if self._dict_to_item(e).start_time.date() == today]
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