from model.todo_model import TodoModel

class CloudSyncHandler:
    def __init__(self, model: TodoModel):
        self._model = model

    def handle_upload_request(self):
        """处理上传到云端的请求"""
        print("🔄 [云同步] 开始上传数据到云端...")
        try:
            success = self._model.sync_upload()
            if success:
                print("✅ [云同步] 上传成功！数据已同步到云端")
            else:
                print("❌ [云同步] 上传失败！请检查网络连接或配置")
        except Exception as e:
            print(f"❌ [云同步] 上传异常: {e}")

    def handle_download_request(self):
        """处理从云端下载的请求"""
        print("🔄 [云同步] 开始从云端下载数据...")
        try:
            success = self._model.sync_download()
            if success:
                print("✅ [云同步] 下载成功！本地数据已更新")
            else:
                print("❌ [云同步] 下载失败！云端可能无数据或网络异常")
        except Exception as e:
            print(f"❌ [云同步] 下载异常: {e}")
