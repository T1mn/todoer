# Config 模块

此模块包含应用程序的所有配置文件，管理系统设置、云服务认证和各种功能参数。

## 功能概述

- **应用设置**: 管理用户界面、主题、语言等基本配置
- **云服务认证**: 存储Google Cloud服务的认证信息
- **计时器配置**: 番茄钟功能的相关设置
- **事件记录**: 用户活动和事件的记录配置

## 文件列表

### `settings.json`
- **功能**: 应用程序主要设置文件
- **包含配置**:
  - 窗口大小和位置
  - 主题设置（深色/浅色模式）
  - 语言和区域设置
  - 用户偏好选项

### `brilliant-balm-465903-g3-e308e8638139.json`
- **功能**: Google Cloud服务账号密钥文件
- **用途**: 
  - 云存储身份验证
  - API调用授权
  - 数据同步权限管理
- **安全级别**: 敏感文件，不应公开

### `timer_settings.json`
- **功能**: 番茄钟计时器配置
- **包含设置**:
  - 默认计时时长
  - 休息时间设置
  - 通知方式配置
  - 自动开始选项

### `event_records.json`
- **功能**: 事件记录配置模板
- **包含设置**:
  - 事件分类定义
  - 记录格式规范
  - 统计周期设置
  - 导出选项配置

## 配置格式

### settings.json 示例结构
```json
{
  "appearance": {
    "theme": "dark",
    "font_size": 12,
    "window_geometry": {...}
  },
  "behavior": {
    "auto_save": true,
    "startup_behavior": "restore_last_session"
  }
}
```

### timer_settings.json 示例结构
```json
{
  "default_duration": 25,
  "break_duration": 5,
  "long_break_duration": 15,
  "notification_enabled": true
}
```

## 使用方式

### 读取配置
```python
import json

# 读取主设置
with open('config/settings.json', 'r') as f:
    settings = json.load(f)

# 读取计时器设置
with open('config/timer_settings.json', 'r') as f:
    timer_config = json.load(f)
```

### 更新配置
```python
# 修改设置
settings['appearance']['theme'] = 'light'

# 保存更改
with open('config/settings.json', 'w') as f:
    json.dump(settings, f, indent=2)
```

## 安全注意事项

### 敏感文件
- `brilliant-balm-465903-g3-e308e8638139.json` 包含私钥信息
- 不应提交到版本控制系统
- 需要限制文件访问权限

### 备份建议
- 定期备份配置文件
- 在更新前创建配置快照
- 验证配置文件格式的有效性

## 依赖关系

- **被依赖**: 所有模块都可能读取配置文件
- **主要使用者**:
  - `cloud/`: 读取认证配置
  - `timer/`: 读取计时器设置
  - `view/`: 读取界面设置
  - `controller/`: 读取行为配置

## 配置管理最佳实践

- 使用JSON格式保证可读性
- 提供默认值作为后备
- 实现配置验证机制
- 支持配置热重载（部分设置） 