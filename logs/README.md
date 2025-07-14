# Logs 模块

此模块负责应用程序的日志管理系统，记录程序运行状态、错误信息和用户操作，为调试和系统监控提供支持。

## 功能概述

- **分级日志**: 按模块分类记录不同级别的日志信息
- **错误追踪**: 详细记录异常和错误信息，便于问题定位
- **性能监控**: 记录系统性能指标和响应时间
- **操作审计**: 跟踪用户操作和数据变更历史

## 目录结构

### `controller/`
- **功能**: 记录控制器层的操作日志
- **内容**:
  - 用户交互事件
  - 数据处理流程
  - 异常处理记录
  - API调用日志

### `model/`
- **功能**: 记录数据模型层的变更日志
- **内容**:
  - 数据CRUD操作
  - 模型状态变更
  - 数据验证错误
  - 存储操作记录

### `timer/`
- **功能**: 记录番茄钟功能的专用日志
- **内容**:
  - 计时器状态变更
  - 会话开始/结束
  - 通知发送记录
  - 设置修改历史

### `utils/`
- **功能**: 记录工具模块的运行日志
- **内容**:
  - AI服务调用
  - 数据转换操作
  - 网络请求记录
  - 外部服务交互

### `view/`
- **功能**: 记录用户界面的事件日志
- **内容**:
  - 界面组件事件
  - 用户输入记录
  - 窗口状态变化
  - 主题切换操作

## 日志格式规范

### 基本格式
```
[TIMESTAMP] [LEVEL] [MODULE] MESSAGE
2024-01-15 10:30:45 INFO controller 用户添加新任务: "完成项目文档"
2024-01-15 10:31:02 ERROR model 数据保存失败: 权限不足
2024-01-15 10:31:15 DEBUG timer 计时器状态变更: RUNNING -> PAUSED
```

### 详细格式
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "module": "controller",
  "function": "add_item",
  "message": "用户添加新任务",
  "data": {
    "task_id": "task_123",
    "content": "完成项目文档",
    "user_id": "user_001"
  }
}
```

## 日志级别

### DEBUG
- **用途**: 详细的调试信息
- **示例**: 函数调用参数、变量状态
- **环境**: 仅在开发环境启用

### INFO
- **用途**: 一般信息记录
- **示例**: 操作成功、状态变更
- **环境**: 所有环境都启用

### WARNING
- **用途**: 警告信息
- **示例**: 性能问题、资源不足
- **环境**: 生产环境重点关注

### ERROR
- **用途**: 错误信息
- **示例**: 异常处理、操作失败
- **环境**: 需要立即处理

### CRITICAL
- **用途**: 严重错误
- **示例**: 系统崩溃、数据丢失
- **环境**: 需要紧急响应

## 日志配置

### 日志器设置
```python
import logging
from utils.logger import module_logger

# 获取模块日志器
logger = module_logger.get_logger('controller')

# 记录不同级别的日志
logger.debug('调试信息')
logger.info('操作成功')
logger.warning('性能警告')
logger.error('操作失败')
logger.critical('严重错误')
```

### 配置文件
```json
{
  "log_level": "INFO",
  "log_format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
  "rotation": {
    "max_size": "10MB",
    "backup_count": 5
  },
  "modules": {
    "controller": "INFO",
    "model": "DEBUG",
    "view": "WARNING"
  }
}
```

## 日志管理

### 文件轮转
- **大小限制**: 单个日志文件最大10MB
- **备份数量**: 保留最近5个备份文件
- **压缩存储**: 旧日志文件自动压缩
- **清理策略**: 30天后自动删除

### 性能考虑
- **异步写入**: 避免阻塞主线程
- **缓冲机制**: 批量写入提高效率
- **级别过滤**: 根据环境调整日志级别
- **格式优化**: 平衡可读性和存储空间

## 使用方式

### 基本日志记录
```python
from utils.logger import module_logger

def example_function():
    logger = module_logger.get_logger('controller')
    
    logger.info('开始执行操作')
    try:
        # 业务逻辑
        result = process_data()
        logger.info(f'操作成功完成: {result}')
    except Exception as e:
        logger.error(f'操作失败: {e}', exc_info=True)
```

### 结构化日志
```python
logger.info('用户操作', extra={
    'user_id': 'user_123',
    'action': 'add_task',
    'task_id': 'task_456',
    'timestamp': datetime.now().isoformat()
})
```

## 监控和分析

### 日志分析工具
- **ELK Stack**: Elasticsearch + Logstash + Kibana
- **本地工具**: grep, awk, 自定义脚本
- **可视化**: 生成图表和报告

### 关键指标
- **错误率**: ERROR和CRITICAL级别日志的比例
- **响应时间**: 操作执行时间统计
- **用户活跃度**: 用户操作频率分析
- **系统健康**: 资源使用情况监控

## 故障排查

### 常见问题
1. **日志文件过大**: 检查轮转配置
2. **性能影响**: 调整日志级别和格式
3. **磁盘空间**: 清理过期日志文件
4. **权限问题**: 确保写入权限正确

### 调试技巧
- 使用grep快速搜索错误
- 按时间范围过滤日志
- 关注异常堆栈信息
- 对比正常和异常情况的日志

## 安全考虑

- **敏感信息**: 避免记录密码、密钥等敏感数据
- **数据脱敏**: 对用户数据进行适当脱敏
- **访问控制**: 限制日志文件的访问权限
- **审计合规**: 满足相关的审计要求 