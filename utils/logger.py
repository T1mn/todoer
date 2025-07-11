import os
import logging
from datetime import datetime
from typing import Optional

class ModuleLogger:
    """模块化日志管理器"""
    
    def __init__(self, log_base_dir: str = "logs"):
        self.log_base_dir = log_base_dir
        self._loggers = {}
        self._ensure_log_directories()
    
    def _ensure_log_directories(self):
        """确保日志目录存在"""
        modules = ['model', 'timer', 'utils', 'view', 'controller']
        for module in modules:
            os.makedirs(os.path.join(self.log_base_dir, module), exist_ok=True)
    
    def get_logger(self, module_name: str, component_name: Optional[str] = None) -> logging.Logger:
        """获取指定模块的日志器"""
        if component_name:
            logger_name = f"{module_name}.{component_name}"
        else:
            logger_name = module_name
            
        if logger_name not in self._loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
            
            # 创建文件处理器
            log_file = os.path.join(
                self.log_base_dir, 
                module_name, 
                f"{datetime.now().strftime('%Y%m%d')}.log"
            )
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 创建格式器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            # 避免重复添加处理器
            if not logger.handlers:
                logger.addHandler(file_handler)
            
            self._loggers[logger_name] = logger
        
        return self._loggers[logger_name]
    
    def log_timer_event(self, event_type: str, message: str):
        """记录计时器事件"""
        logger = self.get_logger('timer', 'events')
        logger.info(f"[{event_type}] {message}")
    
    def log_model_operation(self, operation: str, details: str):
        """记录模型操作"""
        logger = self.get_logger('model', 'operations')
        logger.info(f"[{operation}] {details}")
    
    def log_view_action(self, action: str, details: str):
        """记录视图操作"""
        logger = self.get_logger('view', 'actions')
        logger.info(f"[{action}] {details}")
    
    def log_controller_action(self, action: str, details: str):
        """记录控制器操作"""
        logger = self.get_logger('controller', 'actions')
        logger.info(f"[{action}] {details}")

# 全局日志管理器实例
module_logger = ModuleLogger() 