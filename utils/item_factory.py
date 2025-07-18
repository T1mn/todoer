from model.todo_model import TodoItem
from utils.data_converter import DataConverter
class ItemFactory:
    @staticmethod
    def create_from_clean_text(text: str) -> TodoItem:
        deadline, clean_text = DataConverter.convert_text_to_date(text)
        priority, clean_text = DataConverter.convert_text_to_priority(clean_text)
        category = "default"
        if '#工作' in text or '#work' in text: category = "work"
        elif '#生活' in text or '#life' in text: category = "life"
        elif '#学习' in text or '#study' in text: category = "study"
        for category_tag in ['#工作', '#work', '#生活', '#life', '#学习', '#study']:
            clean_text = clean_text.replace(category_tag, '')
        clean_text = clean_text.strip()
        item = TodoItem(description=clean_text, deadline=deadline, category=category, priority=priority)
        return item