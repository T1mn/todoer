# Cloud 模块

此模块负责应用程序的云端数据同步功能，实现本地数据与Google Cloud Storage的双向同步。

## 功能概述

- **云端存储**: 将本地待办事项和番茄钟数据上传到Google Cloud Storage
- **数据同步**: 支持从云端下载数据，实现多设备数据一致性
- **异步操作**: 使用异步方式进行云端操作，避免阻塞主界面
- **错误处理**: 提供完善的网络异常和认证错误处理机制

## 文件列表

### `cloud_sync.py`
- **核心类**: `CloudSync`
- **主要功能**:
  - `upload_data()`: 上传本地数据到云端
  - `download_data()`: 从云端下载数据到本地
  - `check_connection()`: 检查云端连接状态
- **支持的数据类型**:
  - 待办事项数据 (todo_events.json)
  - 番茄钟事件记录 (timer_events.json)
  - 应用配置信息

### `__init__.py`
- 模块初始化文件
- 导出主要的云同步类和接口

## 依赖关系

### 外部依赖
- `google-cloud-storage`: Google Cloud Storage客户端库
- `google-auth`: Google身份验证库
- `json`: JSON数据处理

### 内部依赖
- `config/`: 读取Google Cloud认证配置
- `data/`: 访问本地数据文件
- `utils/logger`: 记录云同步操作日志

## 配置要求

### 认证文件
- `config/brilliant-balm-465903-g3-e308e8638139.json`: Google Cloud服务账号密钥文件

### 环境变量
- `GOOGLE_APPLICATION_CREDENTIALS`: 指向认证文件的路径（可选）

## 使用方式

```python
from cloud.cloud_sync import CloudSync

# 初始化云同步客户端
sync_client = CloudSync()

# 上传数据到云端
success = sync_client.upload_data("todo_events.json")

# 从云端下载数据
data = sync_client.download_data("todo_events.json")
```

## 错误处理

- **网络连接错误**: 自动重试机制
- **认证失败**: 提供详细的错误信息
- **权限不足**: 检查bucket访问权限
- **文件不存在**: 优雅处理文件缺失情况

## 安全考虑

- 使用Google Cloud IAM进行访问控制
- 数据传输采用HTTPS加密
- 认证文件需要妥善保管，不应提交到版本控制系统 