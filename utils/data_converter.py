from PyQt5.QtCore import QDate
from utils.param import Param
import re

class DataConverter:
    @staticmethod
    def convert_text_to_date(text):
        original_text = text  # 保存原始文本

        matches = re.findall(Param.date_regex, text)
        if len(matches) > 0:
            year, month, day = matches[0]
            # text = text.replace(matches[0], '')  # 去除匹配到的日期字符串
            date = QDate(int(year), int(month), int(day))
            return date, text

        matches = re.findall(Param.days_regex, text)
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
