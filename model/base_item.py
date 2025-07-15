"""
基础项目数据模型模块

定义所有项目类型的抽象基类，遵循单一职责原则，
只负责数据存储和序列化，不包含任何界面显示逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class BaseItem(ABC):
    """所有项目类型的抽象基类
    
    该基类定义了所有项目的共同属性和接口，
    严格遵循数据与视图分离的原则。
    
    Attributes:
        description: 项目描述文本
        category: 项目分类
        created_time: 创建时间
        item_type: 项目类型标识（由子类设置）
    """
    description: str
    category: str = "default"
    created_time: datetime = field(default_factory=datetime.now)
    item_type: str = field(init=False)
    
    def __post_init__(self) -> None:
        """初始化后处理，验证子类是否正确设置了item_type"""
        if not hasattr(self, '_item_type_set'):
            raise NotImplementedError(
                f"子类 {self.__class__.__name__} 必须在 __post_init__ 中设置 item_type"
            )
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """将对象序列化为字典
        
        子类必须实现此方法来定义具体的序列化逻辑。
        基类提供了通用字段的序列化。
        
        Returns:
            包含对象数据的字典
        """
        return {
            "description": self.description,
            "category": self.category,
            "created_time": self.created_time.isoformat(),
            "item_type": self.item_type
        }
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseItem':
        """从字典反序列化对象
        
        子类必须实现此方法来定义具体的反序列化逻辑。
        
        Args:
            data: 包含对象数据的字典
            
        Returns:
            反序列化后的对象实例
        """
        pass
    
    def __str__(self) -> str:
        """返回对象的字符串表示"""
        return f"{self.__class__.__name__}(description='{self.description}', category='{self.category}')"
    
    def __repr__(self) -> str:
        """返回对象的详细字符串表示"""
        return (f"{self.__class__.__name__}("
                f"description='{self.description}', "
                f"category='{self.category}', "
                f"created_time='{self.created_time.isoformat()}', "
                f"item_type='{self.item_type}')") 