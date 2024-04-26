from PyQt5.QtCore import QStandardPaths, Qt, QDate

import json
from todo import TodoListItem , TodoListWidget

# 获取文档目录路径
documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)

# 获取应用程序数据目录路径
app_data_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)

# 获取用户主目录路径
home_path = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
file_path = documents_path + '/.todo.json'
class Data:
    def save_items_to_json(items):
        if not items:
            return
        # 如果没有这个文件，就创建一个
        with open(file_path, 'w') as f:
            pass
        item_list = []
        for item in items:
            item_data = {
                'text': item.text(),
                'createtime': item.createtime.toString(Qt.ISODate) if item.createtime else None,
                'category': item.category,
                'deadline': item.deadline.toString(Qt.ISODate) if item.deadline else None,
                'done': item.checkbox.isChecked(),
                'consume_time': item.consume_time,
                'donetime': item.donetime.toString(Qt.ISODate) if item.donetime else None,
            }
            item_list.append(item_data)

        with open(file_path, 'w') as f:
            json.dump(item_list, f, indent=2)

        print('Items saved to', file_path)
    def load_items_from_json(list_widget):
        try:
            with open(file_path, 'r') as f:
                pass
        except FileNotFoundError:
            return
        
        with open(file_path, 'r') as f:
            item_list = json.load(f)
        if item_list is None:
            return
        list_widget.clear()
        for item_data in item_list:
            # init by json
            item = TodoListItem(item_data, list_widget)
            list_widget.addItem(item)
        print('Items loaded from', file_path)

    def sort_items(list_widget : TodoListWidget):
        checked_items = []
        unchecked_items = []

        # 将项目根据 checkbox 状态分组
        for i in range(list_widget.count()):
            item = list_widget.item(i).clone()
            if item.get_checkbox().isChecked():
                checked_items.append(item)
            else:
                unchecked_items.append(item)

        # 清空列表控件
        list_widget.clear()

        # 添加未选中的项目回到列表控件
        for item in unchecked_items:
            list_widget.addItem(item)

        # 添加已选中的项目回到列表控件
        for item in checked_items:
            list_widget.addItem(item)

