from PyQt5.QtCore import QDate
import re

class DataConverter:
    date_regex = r"#(\d{4}-\d{1,2}-\d{1,2})"
    days_regex = r"(#今天|#明天|#后天|#大后天|#两天后|#三天后|#\d+)"
    priority_regex = r"(#紧急|#urgent|#高|#high|#中|#medium|#低|#low)"

    @staticmethod
    def convert_text_to_date(text):
        original_text = text  # 保存原始文本

        matches = re.findall(DataConverter.date_regex, text)
        if len(matches) > 0:
            year, month, day = matches[0]
            # text = text.replace(matches[0], '')  # 去除匹配到的日期字符串
            date = QDate(int(year), int(month), int(day))
            return date, text

        matches = re.findall(DataConverter.days_regex, text)
        if len(matches) > 0:
            relative_day = matches[0]
            text = text.replace(relative_day, '')  # 去除匹配到的相对日期字符串
            if relative_day == "#今天":
                date = QDate.currentDate()
                print(date)
            elif relative_day == "#明天":
                date = QDate.currentDate().addDays(1)
            elif relative_day == "#后天":
                date = QDate.currentDate().addDays(2)
            elif relative_day == "#大后天":
                date = QDate.currentDate().addDays(3)
            elif relative_day == "#两天后":
                date = QDate.currentDate().addDays(2)
            elif relative_day == "#三天后":
                date = QDate.currentDate().addDays(3)
            else:
                date = QDate.currentDate().addDays(int(relative_day[1:]))
            return date, text

        return None, original_text

    @staticmethod
    def convert_text_to_priority(text):
        """从文本中提取优先级信息"""
        from model.todo_model import Priority
        
        matches = re.findall(DataConverter.priority_regex, text)
        if len(matches) > 0:
            priority_text = matches[0]
            # 移除优先级标识符
            clean_text = text.replace(priority_text, '').strip()
            
            # 映射优先级
            priority_map = {
                '#紧急': Priority.URGENT, '#urgent': Priority.URGENT,
                '#高': Priority.HIGH, '#high': Priority.HIGH,
                '#中': Priority.MEDIUM, '#medium': Priority.MEDIUM,
                '#低': Priority.LOW, '#low': Priority.LOW
            }
            
            priority = priority_map.get(priority_text, Priority.MEDIUM)
            return priority, clean_text
        
        return Priority.MEDIUM, text  # 默认中等优先级
