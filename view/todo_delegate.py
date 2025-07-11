from PyQt5.QtWidgets import QStyledItemDelegate, QStyle, QApplication, QStyleOptionButton
from PyQt5.QtCore import Qt, QModelIndex, QPoint, QDate, QSize, QRect
from PyQt5.QtGui import QColor, QFont, QPen

class TodoDelegate(QStyledItemDelegate):
    """自定义待办事项的渲染代理"""
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config

    def paint(self, painter, option, index: QModelIndex):
        """重写绘制方法"""
        if not index.isValid():
            return
            
        # 获取数据
        item = index.data(Qt.UserRole)
        if not item:
            return

        painter.save()
        
        # 绘制背景
        self._paint_background(painter, option, item)
        
        # 移除复选框绘制，不再需要
        # self._paint_checkbox(painter, option, item)

        # 绘制优先级指示器
        self._paint_priority(painter, option, item)

        # 绘制文本
        self._paint_text(painter, option, item)

        # 绘制截止日期标签
        self._paint_deadline(painter, option, item)

        painter.restore()

    def _paint_background(self, painter, option, item):
        """绘制背景，区分选中状态和分类颜色"""
        rect = option.rect.adjusted(2, 1, -2, -1)  # 添加内边距创建圆角效果
        
        if option.state & QStyle.State_Selected:
            # 选中时使用稍亮的灰色
            painter.setBrush(QColor("#555555"))
        else:
            # 未选中时使用与列表视图背景相同的颜色
            painter.setBrush(QColor("#2E2E2E"))
        
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 4, 4)  # 绘制圆角矩形

    def _paint_checkbox(self, painter, option, item):
        """绘制复选框"""
        check_rect = QStyle.alignedRect(
            Qt.LeftToRight, Qt.AlignLeft | Qt.AlignVCenter,
            QSize(13, 13), option.rect
        )
        check_rect.moveLeft(option.rect.left() + 5)

        opt = QStyleOptionButton()
        opt.rect = check_rect
        opt.state = QStyle.State_Enabled
        opt.state |= (QStyle.State_On if item.done else QStyle.State_Off)
        QApplication.style().drawControl(QStyle.CE_CheckBox, opt, painter)

    def _paint_priority(self, painter, option, item):
        """绘制优先级指示器"""
        from model.todo_model import Priority
        
        # 定义优先级颜色
        priority_colors = {
            Priority.URGENT: "#FF0000",  # 红色
            Priority.HIGH: "#FF8C00",    # 橙色
            Priority.MEDIUM: "#FFD700",  # 金色
            Priority.LOW: "#32CD32"      # 绿色
        }
        
        # 计算文本宽度以确定优先级圆点的位置
        font = QFont(self.config['ui']['font_family'], self.config['ui']['font_size'])
        if item.done:
            font.setStrikeOut(True)
        
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.horizontalAdvance(item.text)
        
        # 计算可用的文本区域
        text_start_x = option.rect.left() + 10  # 左边距
        text_max_width = option.rect.width() - 70  # 为右侧预留空间
        
        # 如果文本太长，将优先级圆点放在右侧固定位置
        if text_width > text_max_width:
            priority_x = option.rect.right() - 60
        else:
            # 文本较短，将优先级圆点放在文本右侧
            priority_x = text_start_x + text_width + 10
            # 确保不会超出右边界
            if priority_x > option.rect.right() - 60:
                priority_x = option.rect.right() - 60
        
        color = QColor(priority_colors.get(item.priority, "#FFD700"))
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        
        # 绘制优先级圆点
        priority_rect = QRect(priority_x, option.rect.top() + 8, 8, 8)
        painter.drawEllipse(priority_rect)

    def _paint_text(self, painter, option, item):
        """绘制任务文本"""
        font = QFont(self.config['ui']['font_family'], self.config['ui']['font_size'])
        
        if item.done:
            # 已完成任务：划线 + 暗淡颜色
            font.setStrikeOut(True)
            painter.setPen(QColor("#666666"))  # 更暗的灰色
        else:
            # 未完成任务：正常样式
            font.setStrikeOut(False)
            painter.setPen(QColor("#E0E0E0"))  # 亮灰色

        painter.setFont(font)
        
        # 计算文本绘制区域，为优先级圆点预留空间
        text_rect = option.rect.adjusted(10, 0, -70, 0)
        
        # 使用省略号处理过长的文本
        font_metrics = painter.fontMetrics()
        elided_text = font_metrics.elidedText(item.text, Qt.ElideRight, text_rect.width())
        
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, elided_text)

    def _paint_deadline(self, painter, option, item):
        """绘制截止日期标签"""
        if not item.deadline or item.done:
            return

        remaining_days = QDate.currentDate().daysTo(item.deadline)
        if remaining_days < 0: color_key = "urgent"
        elif remaining_days == 0: color_key = "high"
        elif remaining_days <= 2: color_key = "medium"
        else: color_key = "low"

        color = QColor(self.config['colors']['priorities'][color_key])
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        
        label_rect = QRect(option.rect.right() - 45, option.rect.top() + 5, 40, 15)
        painter.drawRoundedRect(label_rect, 5, 5)

        painter.setPen(Qt.white)
        painter.drawText(label_rect, Qt.AlignCenter, str(remaining_days))

    def sizeHint(self, option, index: QModelIndex) -> QSize:
        """提供项目的大小提示"""
        size = super().sizeHint(option, index)
        size.setHeight(30)
        return size 