# 模块功能概述 (model)

此模块是 MVC 架构中的 **模型（Model）**，负责管理应用程序的核心数据和业务逻辑。它独立于用户界面，专注于数据的处理、存储和一致性。

## 文件列表及功能

-   `__init__.py`: 将此文件夹标识为 Python 包。
-   `todo_model.py`:
    -   **核心功能**: 定义和管理待办事项（To-Do）列表。它继承自 PyQt5 的 `QAbstractListModel`，以便与 Qt 的模型/视图框架无缝集成。
    -   **数据管理**: 内部维护一个 `todo_items` 列表，其中每个元素都是一个包含待办事项内容、状态和截止日期的字典。
    -   **业务逻辑**: 实现了添加、删除、排序、保存和加载待办事项的全部逻辑。
    -   **视图通知**: 在数据发生变化时（如添加或删除项），它会发出标准信号（如 `beginInsertRows` / `endInsertRows`），通知所有关联的视图（View）更新显示，确保数据的一致性。

## 外部关系

-   **被 `controller` 依赖**: `AppController` 会创建并持有一个 `TodoModel` 的实例，调用其公共方法（如 `add_item`）来修改数据。
-   **为 `view` 提供数据**: `MainWindow` 中的 `QListView` 和 `TodoDelegate` 直接绑定到此模型。当视图需要显示或绘制数据时，会通过 `data()` 方法从模型中获取信息。 