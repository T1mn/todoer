import json
import os
from enum import Enum
from PySide6.QtCore import QObject, Signal, QTimer
from model.event_model import EventModel
from cloud.cloud_sync import CloudSync

class TimerStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"

class TimerModel(QObject):
    time_updated = Signal(int)
    timer_finished = Signal()
    status_changed = Signal(str)
    event_record_requested = Signal(int)

    def __init__(self, user_id, key_path):
        super().__init__()
        self.total_seconds = 900
        self.remaining_seconds = 900
        self.status = TimerStatus.STOPPED
        self._qtimer = QTimer()
        self._qtimer.timeout.connect(self._update_time)
        self._qtimer.setInterval(1000)
        self.event_model = EventModel(user_id, key_path)
        self._session_active = False
        self.user_id = user_id
        self.key_path = key_path
        self._data_dir = 'data'
        self._data_file_path = os.path.join(self._data_dir, 'timer_events.json')
        self._collection_name = 'timer_events'
        self._cloud = CloudSync(key_path, user_id)
        self._ensure_local_file_exists()
        self.data = self._load_from_local()

    def _ensure_local_file_exists(self):
        os.makedirs(self._data_dir, exist_ok=True)
        if not os.path.exists(self._data_file_path):
            with open(self._data_file_path, 'w', encoding='utf-8') as f:
                json.dump({"events": []}, f)

    def _load_from_local(self) -> dict:
        with open(self._data_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_to_local(self):
        with open(self._data_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def sync_upload(self) -> bool:
        self.save_to_local()
        return self._cloud.upload(self._collection_name, self._data_file_path)

    def sync_download(self) -> bool:
        if self._cloud.download(self._collection_name, self._data_file_path):
            self.data = self._load_from_local()
            return True
        return False

    def set_timer(self, seconds: int):
        if self.status == TimerStatus.RUNNING:
            return
        self.total_seconds = max(60, min(10800, seconds))
        self.remaining_seconds = self.total_seconds
        self.status = TimerStatus.STOPPED
        self.time_updated.emit(self.remaining_seconds)
        self.status_changed.emit(self.status.value)

    def start_timer(self):
        if self.status not in [TimerStatus.STOPPED, TimerStatus.PAUSED]:
            return
        self.status = TimerStatus.RUNNING
        self._qtimer.start()
        if not self._session_active:
            self.event_model.start_session()
            self._session_active = True
        self.status_changed.emit(self.status.value)

    def pause_timer(self):
        if self.status != TimerStatus.RUNNING:
            return
        self.status = TimerStatus.PAUSED
        self._qtimer.stop()
        self.status_changed.emit(self.status.value)

    def stop_timer(self):
        if self.status not in [TimerStatus.RUNNING, TimerStatus.PAUSED]:
            return
        self.status = TimerStatus.STOPPED
        self._qtimer.stop()
        completed_minutes = (self.total_seconds - self.remaining_seconds) // 60
        self.remaining_seconds = self.total_seconds
        self.time_updated.emit(self.remaining_seconds)
        self.status_changed.emit(self.status.value)
        if self._session_active and completed_minutes >= 1:
            self.event_record_requested.emit(completed_minutes)
        self._session_active = False

    def _update_time(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.time_updated.emit(self.remaining_seconds)
        else:
            self._qtimer.stop()
            self.status = TimerStatus.FINISHED
            self.status_changed.emit(self.status.value)
            completed_minutes = self.total_seconds // 60
            self.timer_finished.emit()
            if self._session_active:
                self.event_record_requested.emit(completed_minutes)
            self._session_active = False

    def record_event(self, event_description: str, category: str = "default"):
        if self.event_model.current_session_start:
            return self.event_model.end_session(event_description, category)
        return None

    def get_button_text(self) -> str:
        if self.status == TimerStatus.RUNNING:
            return f"⏰ {self.remaining_seconds // 60:02d}:{self.remaining_seconds % 60:02d}"
        if self.status == TimerStatus.PAUSED:
            return f"⏸ {self.remaining_seconds // 60:02d}:{self.remaining_seconds % 60:02d}"
        if self.status == TimerStatus.FINISHED:
            return "✅ 完成"
        return f"Timer {self.total_seconds // 60}m"
