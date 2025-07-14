# Model 模块

此模块是 MVC 架构中的 **模型（Model）**，负责管理应用程序的核心数据和业务逻辑。它独立于用户界面，专注于数据的处理、存储和一致性。

## 功能概述

- **数据管理**: 管理应用程序的核心业务数据
- **业务逻辑**: 实现数据验证、处理和转换的业务规则
- **持久化**: 提供数据的保存和加载功能
- **状态管理**: 维护数据的一致性和完整性
- **事件通知**: 通过信号机制通知数据变更

## 文件列表及功能

### `base_model.py`
- **核心类**: `BaseModel`
- **主要功能**:
  - 提供所有模型类的基础功能
  - 定义通用的数据操作接口
  - 实现基本的持久化机制
  - 提供数据验证框架

### `todo_model.py`
- **核心类**: `TodoModel`, `TodoItem`
- **主要功能**:
  - 管理待办事项列表数据
  - 继承自 `QAbstractListModel`，与Qt模型/视图框架集成
  - 实现添加、删除、修改、排序等操作
  - 支持优先级、类别、截止日期等属性
  - 提供数据的自动保存和加载
- **数据结构**:
  - `TodoItem`: 单个待办事项的数据模型
  - 包含文本、状态、优先级、类别、截止日期等属性

### `event_model.py`
- **核心类**: `EventModel`, `Event`
- **主要功能**:
  - 管理用户活动事件数据
  - 记录用户操作历史
  - 支持事件分类和统计
  - 提供事件查询和筛选功能

### `timer_model.py`
- **核心类**: `TimerModel`, `TimerStatus`
- **主要功能**:
  - 管理番茄钟计时器的状态和数据
  - 实现计时逻辑和状态转换
  - 记录计时会话历史
  - 支持云端数据同步
  - 提供今日统计和分析功能
- **状态管理**:
  - `STOPPED`: 停止状态
  - `RUNNING`: 运行状态
  - `PAUSED`: 暂停状态

## 数据模型设计

### TodoItem 数据结构
```python
class TodoItem:
    def __init__(self):
        self.id: str           # 唯一标识符
        self.text: str         # 任务内容
        self.done: bool        # 完成状态
        self.priority: str     # 优先级 (low/medium/high/urgent)
        self.category: str     # 类别 (work/life/study/default)
        self.deadline: QDate   # 截止日期
        self.created_at: QDateTime  # 创建时间
        self.tags: List[str]   # 标签列表
```

### Event 数据结构
```python
class Event:
    def __init__(self):
        self.id: str                # 事件ID
        self.timestamp: QDateTime   # 事件时间
        self.event_type: str        # 事件类型
        self.description: str       # 事件描述
        self.category: str          # 事件分类
        self.duration: int          # 持续时间（分钟）
        self.metadata: Dict         # 额外元数据
```

## Qt模型/视图集成

### QAbstractListModel
- `TodoModel` 继承自 `QAbstractListModel`
- 实现标准的模型接口方法：
  - `rowCount()`: 返回数据行数
  - `data()`: 返回指定索引的数据
  - `setData()`: 设置指定索引的数据
  - `flags()`: 返回项目标志
  - `insertRows()`: 插入新行
  - `removeRows()`: 删除行

### 信号机制
- `beginInsertRows()` / `endInsertRows()`: 插入数据前后通知
- `beginRemoveRows()` / `endRemoveRows()`: 删除数据前后通知
- `dataChanged()`: 数据变更通知
- 自定义信号：`itemAdded`, `itemRemoved`, `itemModified`

## 业务逻辑

### 数据验证
- 任务内容非空验证
- 截止日期合理性检查
- 优先级和类别有效性验证
- 重复任务检测

### 自动处理
- 过期任务自动标记
- 优先级自动调整
- 智能分类建议
- 数据格式标准化

### 排序和筛选
- 按优先级排序
- 按截止日期排序
- 按创建时间排序
- 按类别筛选
- 按完成状态筛选

## 持久化机制

### 数据格式
- 使用JSON格式存储数据
- 支持数据版本管理
- 提供数据迁移功能

### 保存策略
- 自动保存：数据变更时自动保存
- 延迟保存：避免频繁I/O操作
- 批量保存：提高保存效率
- 备份机制：定期创建数据备份

### 加载机制
- 启动时自动加载数据
- 数据完整性验证
- 错误恢复机制
- 默认数据初始化

## 数据同步

### 云端同步
- 支持与Google Cloud Storage同步
- 冲突解决策略
- 离线数据缓存
- 增量同步优化

### 多设备同步
- 设备标识管理
- 数据合并算法
- 版本控制机制
- 同步状态跟踪

## 外部关系

### 被依赖关系
- **Controller层**: `AppController` 调用模型方法进行数据操作
- **View层**: `QListView` 绑定模型显示数据，`TodoDelegate` 获取数据进行渲染

### 依赖关系
- **Utils层**: 使用数据转换工具和AI服务
- **Config层**: 读取配置文件
- **Data层**: 访问本地数据文件

## 性能优化

### 内存管理
- 延迟加载大量数据
- 使用弱引用避免循环引用
- 及时释放不需要的对象

### 操作优化
- 批量操作减少通知次数
- 索引优化提高查询效率
- 缓存机制减少重复计算

### 数据结构优化
- 使用适当的数据结构
- 预计算常用统计数据
- 数据分页处理大数据集

## 错误处理

### 数据异常
- 格式错误自动修复
- 数据丢失恢复机制
- 版本不兼容处理
- 损坏文件修复

### 操作异常
- 非法操作阻止
- 状态不一致修复
- 并发操作处理
- 事务回滚机制

## 扩展性设计

### 插件机制
- 支持自定义数据字段
- 可扩展的业务规则
- 动态加载数据处理器

### 接口设计
- 定义标准的数据操作接口
- 支持多种数据源适配
- 提供数据导入导出接口

## 测试支持

### 单元测试
- 数据操作方法测试
- 业务逻辑验证
- 边界条件测试

### 数据测试
- 大数据量性能测试
- 数据完整性测试
- 并发操作测试

### Mock支持
- 提供测试数据生成器
- 支持外部依赖Mock
- 状态隔离测试环境 