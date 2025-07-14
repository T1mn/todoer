from model.todo_model import TodoModel, TodoItem
from utils.ai_service import GeminiService
from utils.ai_converter import AIConverter

class AIParseHandler:
    def __init__(self, model: TodoModel, ai_service: GeminiService):
        self._model = model
        self._ai_service = ai_service

    def parse_item(self, text: str):
        if not self._ai_service or not self._ai_service.is_available():
            self._fallback_add_item(text)
            return
        try:
            ai_result = self._ai_service.parse_todo_text(text)
            todo_item = AIConverter.convert_ai_to_todo_item(ai_result)
            self._model.add_item(todo_item)
        except Exception as e:
            print(f"AI 解析失败，回退到普通解析: {e}")
            self._fallback_add_item(text)

    def _fallback_add_item(self, text: str):
        # This is a simplified version of the original add_item logic.
        # A more robust solution would be to have a shared utility for this.
        from utils.data_converter import DataConverter
        deadline, clean_text = DataConverter.convert_text_to_date(text)
        priority, clean_text = DataConverter.convert_text_to_priority(clean_text)
        item = TodoItem(text=clean_text, deadline=deadline, priority=priority)
        self._model.add_item(item)
