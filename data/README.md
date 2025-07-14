# Data 模块

此模块负责应用程序的本地数据存储，管理待办事项、计时器事件和其他持久化数据。

## 功能概述

- **数据持久化**: 将应用程序状态保存到本地文件
- **格式管理**: 使用JSON格式确保数据的可读性和可移植性
- **数据完整性**: 提供数据备份和恢复机制
- **版本兼容**: 支持数据格式的向前兼容

## 文件列表

### `todo_events.json`
- **功能**: 存储待办事项的完整数据
- **数据结构**:
  - 任务ID和内容
  - 创建时间和截止日期
  - 完成状态和优先级
  - 类别和标签信息
- **更新频率**: 实时更新，每次任务变更时保存

### `timer_events.json`
- **功能**: 存储番茄钟事件记录
- **数据结构**:
  - 会话开始和结束时间
  - 任务描述和分类
  - 中断次数和原因
  - 效率评估数据
- **更新频率**: 每次番茄钟会话结束时记录

### `event_records.json`
- **功能**: 存储用户活动的综合记录
- **数据结构**:
  - 事件类型和时间戳
  - 用户操作记录
  - 系统状态变更
  - 性能指标数据
- **更新频率**: 根据事件类型实时或定期更新

## 数据格式规范

### todo_events.json 结构
```json
{
  "version": "1.0",
  "last_updated": "2024-01-15T10:30:00Z",
  "items": [
    {
      "id": "unique_id",
      "text": "任务描述",
      "created_at": "2024-01-15T09:00:00Z",
      "deadline": "2024-01-16T18:00:00Z",
      "priority": "high",
      "category": "work",
      "completed": false,
      "tags": ["urgent", "project-a"]
    }
  ]
}
```

### timer_events.json 结构
```json
{
  "version": "1.0",
  "sessions": [
    {
      "id": "session_id",
      "start_time": "2024-01-15T09:00:00Z",
      "end_time": "2024-01-15T09:25:00Z",
      "duration_minutes": 25,
      "task_description": "完成项目文档",
      "category": "work",
      "interruptions": 0,
      "efficiency_rating": 4
    }
  ]
}
```

## 数据操作

### 读取数据
```python
import json
from pathlib import Path

def load_todo_data():
    data_file = Path("data/todo_events.json")
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "1.0", "items": []}
```

### 保存数据
```python
def save_todo_data(data):
    data["last_updated"] = datetime.now().isoformat()
    with open("data/todo_events.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

## 数据管理策略

### 备份机制
- 每日自动备份重要数据文件
- 保留最近7天的备份版本
- 支持手动创建数据快照

### 数据同步
- 与云端存储保持同步
- 冲突解决策略：以最新时间戳为准
- 离线模式支持本地数据操作

### 性能优化
- 增量更新减少I/O操作
- 数据索引提高查询效率
- 延迟写入避免频繁磁盘访问

## 依赖关系

### 数据提供者
- `model/`: 数据模型层的持久化实现
- `controller/`: 控制器触发的数据保存操作

### 数据消费者
- `cloud/`: 云同步时读取本地数据
- `view/`: 界面显示时加载数据
- `utils/`: 数据分析和统计功能

## 错误处理

### 文件损坏
- 自动检测JSON格式错误
- 从备份文件恢复数据
- 提供数据修复工具

### 磁盘空间
- 监控可用磁盘空间
- 清理过期的备份文件
- 压缩历史数据

## 数据迁移

### 版本升级
- 检测数据格式版本
- 自动执行迁移脚本
- 保留原始数据作为备份

### 格式转换
- 支持导入其他格式的数据
- 提供数据导出功能
- 确保数据完整性验证 