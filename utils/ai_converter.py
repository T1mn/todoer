from PyQt5.QtCore import QDate
from model.todo_model import TodoItem, Priority
from utils.ai_service import TodoItemAI, PriorityLevel, CategoryType

class AIConverter:
    """AI 数据转换器"""
    
    @staticmethod
    def convert_ai_to_todo_item(ai_item: TodoItemAI) -> TodoItem:
        """将 AI 解析的数据转换为 TodoItem"""
        
        # 转换优先级
        priority_map = {
            PriorityLevel.LOW: Priority.LOW,
            PriorityLevel.MEDIUM: Priority.MEDIUM,
            PriorityLevel.HIGH: Priority.HIGH,
            PriorityLevel.URGENT: Priority.URGENT
        }
        priority = priority_map.get(ai_item.priority, Priority.MEDIUM)
        
        # 转换类别
        category_map = {
            CategoryType.DEFAULT: "default",
            CategoryType.WORK: "work",
            CategoryType.LIFE: "life",
            CategoryType.STUDY: "study"
        }
        category = category_map.get(ai_item.category, "default")
        
        # 转换截止日期
        deadline = None
        if ai_item.deadline:
            try:
                # 假设 AI 返回的日期格式是 YYYY-MM-DD
                year, month, day = ai_item.deadline.split('-')
                deadline = QDate(int(year), int(month), int(day))
            except (ValueError, AttributeError):
                deadline = None
        
        # 创建 TodoItem
        todo_item = TodoItem(
            text=ai_item.text,
            priority=priority,
            category=category,
            deadline=deadline
        )
        
        # 如果有预估时间，可以存储在 consume_time 字段中
        if ai_item.estimated_time:
            todo_item.consume_time = ai_item.estimated_time
        
        return todo_item 