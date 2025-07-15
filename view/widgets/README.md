# 控件 (Widgets)

此目录包含可复用的、独立的 UI 组件。

## 模块

- **ai_line_edit.py**: `QLineEdit` 的子类，支持用于 AI 文本解析的特殊按键组合（例如，Shift+Enter）。
- **todo_list_view.py**: 用于显示待办事项列表的 `TodoListView`，继承自 `BaseListView`。
- **time_list_view.py**: 用于显示已完成时间记录的 `TimeListView`，继承自 `BaseListView`。
- **base_list_view.py**: 所有列表视图的基类，提供统一的Material Design样式和交互行为。
- **list_toggle_buttons.py**: Material Design风格的切换按钮组，用于在Todo List和Time List之间切换。

## 新增功能 - Time List

### 功能特性
- **时间记录展示**: 显示已完成的番茄钟时间记录
- **Material Design样式**: 遵循Google Material Design设计规范
- **统一交互体验**: 与Todo List保持一致的操作体验
- **实时数据更新**: 完成番茄钟后自动刷新显示
- **模式切换**: 通过切换按钮在Todo和Time模式间切换

### 组件说明

#### BaseListView
- **功能**: 所有列表视图的基类
- **特性**: 
  - 统一的Material Design样式
  - 右键菜单支持
  - Delete键删除功能
  - 双击事件处理
- **继承**: 被TodoListView和TimeListView继承

#### TimeListView
- **功能**: 显示已完成的时间记录
- **数据源**: EventModel中的事件记录
- **显示格式**: 时间 | 类别 | 持续时间 + 事件描述
- **排序**: 按完成时间倒序排列

#### ListToggleButtons
- **功能**: Todo/Time模式切换按钮
- **样式**: Material Design Toggle Button规范
- **交互**: 互斥选择，支持程序化切换
- **信号**: mode_changed信号通知模式变更

### 使用方法

1. **切换到Time List**: 点击输入框右侧的"🕐 Time"按钮
2. **查看时间记录**: 列表显示所有已完成的番茄钟记录
3. **切换回Todo List**: 点击"📝 Todo"按钮返回待办事项列表
4. **右键菜单**: 支持查看详情和删除操作

### 技术实现

- **最小化变更**: 保持现有代码结构，通过继承和组合实现新功能
- **公用基类**: TodoListView和TimeListView都继承自BaseListView
- **模式切换**: 使用QStackedWidget管理两个列表视图的切换
- **数据同步**: TimeListView自动响应EventModel的数据变更

### 设计原则

- **Google Material Design**: 遵循Material Design色彩、间距和交互规范
- **一致性**: 与现有Todo List保持一致的视觉风格和操作体验
- **可扩展性**: 基于BaseListView的设计便于未来扩展更多列表类型
- **响应式**: 支持不同窗口大小的自适应显示