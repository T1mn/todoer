def load_stylesheet(path: str) -> str:
    """从文件加载样式表"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
