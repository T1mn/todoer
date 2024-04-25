from PyQt5.QtGui import QColor
# import QtPoint
from PyQt5.QtCore import Qt
class Param:
    opacity = 0.7
    red = QColor(255, 0, 0)
    green = QColor(0, 128, 0)
    blue = QColor(0, 0, 128)
    yellow = QColor(255, 215, 0)
    orange = QColor(255, 165, 0)
    purple = QColor(128, 0, 128)
    gray = QColor(128, 128, 128)
    white = QColor(255, 255, 255)
    black = QColor(0, 0, 0)
    item_width = 10
    item_height = 30
    window_width = 200
    window_height = 300
    status_bar_height = 20
    date_regex = r"(?P<year>\d{4})[年/](?P<month>\d{1,2})[月/](?P<day>\d{1,2})[日]?"
    days_regex = r"(?P<relativedate>(?:#今天|#明天|#后天|#大后天|#两天后|#三天后|#\d+天后))"
