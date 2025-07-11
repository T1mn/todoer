import sys
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QStandardPaths
from PyQt5.Qt import Qt

from model.todo_model import TodoModel
from view.main_window import MainWindow
from view.todo_delegate import TodoDelegate
from controller.app_controller import AppController

def load_config(path='config/settings.json'):
    """加载JSON配置文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        sys.exit(f"Error: Configuration file '{path}' not found or invalid.")

def main():
    """应用程序主入口"""
    # 在创建 QApplication 之前设置属性
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)

    # 确保当最后一个窗口关闭时，应用程序也会退出
    app.setQuitOnLastWindowClosed(True)

    # 1. 加载配置
    config = load_config()

    # 2. 设置数据文件路径
    docs_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
    file_path = f"{docs_path}/{config['data']['storage_file']}"

    # 3. 初始化MVC组件
    model = TodoModel(file_path)
    view = MainWindow(config)
    delegate = TodoDelegate(config)
    controller = AppController(model, view)

    # 4. 连接组件
    view.list_view.setModel(model)
    view.list_view.setItemDelegate(delegate)
    
    # 5. 加载初始数据并显示
    model.load()
    view.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 