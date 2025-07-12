import sys
import json
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QStandardPaths, qInstallMessageHandler, QtMsgType
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.Qt import Qt

from model.todo_model import TodoModel
from view.main_window import MainWindow
from view.todo_delegate import TodoDelegate
from controller.app_controller import AppController

def qt_message_handler(mode, context, message):
    """自定义Qt消息处理器，过滤掉特定的警告信息"""
    # 过滤掉QFileSystemWatcher的警告信息
    if "QFileSystemWatcher::removePaths: list is empty" in message:
        return  # 忽略这个警告
    
    # 其他消息正常输出
    if mode == QtMsgType.QtDebugMsg:
        print(f"Qt Debug: {message}")
    elif mode == QtMsgType.QtWarningMsg:
        print(f"Qt Warning: {message}")
    elif mode == QtMsgType.QtCriticalMsg:
        print(f"Qt Critical: {message}")
    elif mode == QtMsgType.QtFatalMsg:
        print(f"Qt Fatal: {message}")

def load_config(path='config/settings.json'):
    """加载JSON配置文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"警告：配置文件加载失败 ({e})，使用默认配置")
        # 返回默认配置
        return {
            "ui": {
                "opacity": 0.9,
                "window_width": 300,
                "window_height": 400,
                "status_bar_height": 10,
                "font_family": "Arial",
                "font_size": 10
            },
            "colors": {
                "priorities": {
                    "urgent": "rgb(255, 0, 0)",
                    "high": "rgb(255, 165, 0)",
                    "medium": "rgb(255, 215, 0)",
                    "low": "rgb(0, 128, 0)"
                }
            },
            "data": {
                "storage_file": ".todo.json"
            }
        }

def main():
    """应用程序主入口"""
    try:
        # 安装自定义消息处理器
        qInstallMessageHandler(qt_message_handler)
        
        # 在创建 QApplication 之前设置属性
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)

        # ------------------- 字体加载与设置（核心修改） -------------------
        font_path = os.path.join(os.path.dirname(__file__), 'resources', 'WenQuanYi Micro Hei.ttf')
        font_id = QFontDatabase.addApplicationFont(font_path)
        
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                app_font = QFont(font_families[0], 10) # 使用加载的字体族，10为默认字号
                app.setFont(app_font)
                print(f"全局字体已成功设置为: {font_families[0]}") # 添加成功日志
            else:
                print("警告：字体已加载但无法获取字体族名称，将使用系统默认字体。")
        else:
            print(f"警告：字体文件加载失败，路径: {font_path}，将使用系统默认字体。")
        # -----------------------------------------------------------------

        # 修改退出策略：只有在明确请求时才退出，避免因对话框关闭导致意外退出
        app.setQuitOnLastWindowClosed(False)

        # 1. 加载配置
        config = load_config()

        # 2. 设置数据文件路径
        docs_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        file_path = f"{docs_path}/{config['data']['storage_file']}"
        
        # 确保文档目录存在
        os.makedirs(docs_path, exist_ok=True)

        # 3. 初始化MVC组件
        model = TodoModel(file_path)
        view = MainWindow(config)
        delegate = TodoDelegate(config)
        controller = AppController(model, view)

        # 4. 连接组件
        view.list_view.setModel(model)
        view.list_view.setItemDelegate(delegate)
        
        # 5. 加载初始数据并显示
        try:
            model.load()
        except Exception as e:
            print(f"警告：数据加载失败 ({e})，将从空列表开始")
            
        view.show()

        # 运行应用程序
        exit_code = app.exec_()
        
        # 退出前保存数据
        try:
            model.save()
        except Exception as e:
            print(f"警告：退出时保存数据失败 ({e})")
            
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 