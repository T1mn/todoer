from view.widgets.base_list_view import BaseListView


class TodoListView(BaseListView):
    """
    待办事项列表视图
    继承BaseListView的所有通用功能
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def get_display_name(self) -> str:
        """返回列表类型名称"""
        return "待办事项"

    def get_empty_message(self) -> str:
        """返回空列表时的提示信息"""
        return "暂无待办事项\n点击上方输入框添加新任务"

    def handle_empty_state(self):
        """处理空列表状态显示"""
        # 可以在这里添加空状态的特殊处理
        pass 