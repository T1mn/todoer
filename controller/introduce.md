# 模块功能概述 (controller)

此模块是 MVC 架构中的 **控制器（Controller）**，扮演着模型（Model）和视图（View）之间的“交通警察”或“胶水”角色。它不处理具体的数据（模型的工作）或用户界面（视图的工作），而是协调两者，确保整个应用程序正确响应用户操作。

## 文件列表及功能

-   `__init__.py`: 将此文件夹标识为 Python 包。
-   `app_controller.py`:
    -   **核心功能**: `AppController` 是应用的总指挥。它在启动时创建 `TodoModel` 和 `MainWindow` 的实例。
    -   **绑定模型与视图**: 它将 `TodoModel` 实例设置给 `MainWindow` 中的 `QListView`，并将 `TodoDelegate` 实例也设置给 `QListView`，从而将数据、渲染和UI显示三者绑定在一起。
    -   **信号处理**: 它连接（`connect`）来自 `MainWindow` 的信号（如 `add_item_requested`）到自己的处理方法（槽函数）上。

## MVC 协同工作流程示例

以 **“用户添加一个新的待办事项”** 为例，看各模块如何协同工作：

1.  **视图 (View)**: 用户在 `MainWindow` 的输入框中输入文字，然后按回车键。
    -   `main_window.py` 内部的 `input_lineedit` 控件发出 `returnPressed` 信号。
    -   `MainWindow` 捕获此信号，并调用自己的 `_on_add_item` 方法。
    -   该方法随即发射一个更高级别的信号 `add_item_requested`，并附带用户输入的文本。视图的工作到此结束，它不知道接下来会发生什么。

2.  **控制器 (Controller)**: `AppController` 一直在监听 `add_item_requested` 信号。
    -   当信号到达时，`AppController` 中对应的处理方法被触发。
    -   控制器调用 **模型** 的 `model.add_item(text)` 方法，将用户的请求和数据传递给模型。

3.  **模型 (Model)**: `TodoModel` 接收到 `add_item` 的调用。
    -   它执行业务逻辑：将新数据处理并添加到内部的 `todo_items` 列表中。
    -   在列表更新前后，它会发射 `beginInsertRows` 和 `endInsertRows` 信号。这是 Qt 模型/视图框架的标准做法。

4.  **视图 (View) 自动更新**:
    -   `MainWindow` 中的 `QListView` 因为已经和 `TodoModel` 绑定，所以它会自动接收到 `rowsInserted` 信号。
    -   `QListView` 知道数据已更新，因此它会重新查询模型获取新数据，并请求 `TodoDelegate` 来绘制新的列表项。

这个流程完美地展示了 **关注点分离** 的原则：视图只管显示和采集用户输入，模型只管处理数据和业务规则，而控制器则负责协调它们之间的通信。 