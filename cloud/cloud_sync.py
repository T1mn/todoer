import os
import threading
from typing import Callable
import json
import firebase_admin
from firebase_admin import credentials, firestore

class CloudSync:
    def __init__(self, key_path: str, user_id: str):
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.user_id = user_id
        self.listeners = {}

    def upload(self, collection: str, local_path: str) -> bool:
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            doc_ref = self.db.collection(collection).document(self.user_id)
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"[CloudSync] 上传失败: {e}")
            return False

    def download(self, collection: str, local_path: str) -> bool:
        try:
            doc_ref = self.db.collection(collection).document(self.user_id)
            doc = doc_ref.get()
            if doc.exists:
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2)
                return True
            else:
                print(f"[CloudSync] 云端无数据: {collection}/{self.user_id}")
                return False
        except Exception as e:
            print(f"[CloudSync] 下载失败: {e}")
            return False

    def start_listener(self, collection: str, callback: Callable):
        doc_ref = self.db.collection(collection).document(self.user_id)
        def on_snapshot(doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                callback(doc.to_dict())
        # Firestore 监听器需在新线程中启动，避免阻塞主线程
        listener = doc_ref.on_snapshot(on_snapshot)
        self.listeners[collection] = listener

    def stop_listener(self, collection: str):
        listener = self.listeners.get(collection)
        if listener:
            listener.unsubscribe()
            del self.listeners[collection] 