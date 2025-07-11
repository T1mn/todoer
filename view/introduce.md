# 模块功能概述 (view)

此模块是 MVC 架构中的 **视图（View）**，负责构建和管理用户界面（UI）。它将模型（Model）中的数据显示给用户，并捕获用户的交互操作（如点击、输入等）。

## 文件列表及功能

-   `__init__.py`: 将此文件夹标识为 Python 包。
-   `main_window.py`:
    -   **核心功能**: 定义应用程序的主窗口 `MainWindow`，包含输入框、按钮和待办事项列表（`QListView`）等所有UI控件。
    -   **用户交互**: 负责监听用户的原生UI事件（如按钮点击、键盘回车），并将这些事件转化为抽象的业务请求信号（如 `add_item_requested`）。它本身不处理业务逻辑，只负责“通知”外界用户的意图。
-   `todo_delegate.py`:
    -   **核心功能**: 这是本应用视图层的一个关键组件，继承自 `QStyledItemDelegate`，专门用于**自定义 `QListView` 中每一个列表项的渲染方式**。
    -   **为何需要它**: 如果没有 `Delegate`，`QListView` 只能显示简单的文本字符串。`TodoDelegate` 允许我们将每个待办事项渲染成包含多行文本、不同颜色和图标的复杂布局。
    -   **工作原理**:
        1.  **`paint()` 方法**: 当 `QListView` 需要绘制某个列表项时，会调用此方法。方法内部通过 `index.data()` 从模型中获取该项的完整数据（内容、日期、状态等）。然后，它使用 `QPainter` 工具，像在画布上画画一样，精确地在列表项的矩形区域内绘制文本、线条和状态指示器，从而实现丰富的视觉效果。
        2.  **`sizeHint()` 方法**: `QListView` 通过调用此方法来查询每个列表项应该占据多大的空间（特别是高度）。这使得列表项可以根据内容动态调整大小，而不是所有项都具有固定的高度。

## 外部关系

-   **依赖 `model`**: 视图中的 `QListView` 和 `TodoDelegate` 直接与 `TodoModel` 关联，以便在需要时获取数据进行显示和绘制。
-   **被 `controller` 依赖**: `AppController` 创建并管理 `MainWindow` 实例，并将 `TodoDelegate` 设置给 `QListView`。
-   **与 `controller` 交互**: `MainWindow` 通过发射信号（如 `sort_items_requested`）来通知 `AppController` 用户的操作请求。

## 相互关系

`main_window.py` 构成了应用的骨架，而 `todo_delegate.py` 则是血肉，它让列表中的每一个细胞（列表项）都变得生动和具体。两者共同协作，为用户呈现一个功能完整且视觉丰富的界面。 