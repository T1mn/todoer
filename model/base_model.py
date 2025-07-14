import json
import os
from typing import List, Any, Callable
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from cloud.cloud_sync import CloudSync

class BaseModel(QAbstractListModel):
    def __init__(self, user_id: str, key_path: str, data_file: str, collection_name: str):
        super().__init__()
        self.user_id = user_id
        self._data_dir = 'data'
        self._data_file_path = os.path.join(self._data_dir, data_file)
        self._collection_name = collection_name
        self._cloud = CloudSync(key_path, user_id)
        self._items: List[Any] = []
        self._ensure_local_file_exists()
        self.load()

    def _ensure_local_file_exists(self):
        os.makedirs(self._data_dir, exist_ok=True)
        if not os.path.exists(self._data_file_path):
            with open(self._data_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.get_default_data_structure(), f)

    def get_default_data_structure(self) -> dict:
        return {'items': []}

    def load(self):
        try:
            with open(self._data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.beginResetModel()
            items_data = data.get('items', data.get('events', []))
            self._items = [self._dict_to_item(item_data) for item_data in items_data]
            self.endResetModel()
        except (FileNotFoundError, json.JSONDecodeError):
            self._items = []

    def save(self):
        with open(self._data_file_path, 'w', encoding='utf-8') as f:
            data = {'items': [self._item_to_dict(item) for item in self._items]}
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _dict_to_item(self, data: dict) -> Any:
        raise NotImplementedError("Subclasses must implement _dict_to_item")

    def _item_to_dict(self, item: Any) -> dict:
        raise NotImplementedError("Subclasses must implement _item_to_dict")

    def sync_upload(self):
        self.save()
        return self._cloud.upload(self._collection_name, self._data_file_path)

    def sync_download(self):
        if self._cloud.download(self._collection_name, self._data_file_path):
            self.load()
            return True
        return False

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return None
        item = self._items[index.row()]
        if role == Qt.DisplayRole:
            return getattr(item, 'text', '')
        elif role == Qt.UserRole:
            return item
        return None
