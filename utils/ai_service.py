import os
import json
from typing import Optional
from datetime import date
from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai

# 加载环境变量
load_dotenv()

class PriorityLevel(str, Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class CategoryType(str, Enum):
    """类别枚举"""
    DEFAULT = "default"
    WORK = "work"
    LIFE = "life"
    STUDY = "study"

class TodoItemAI(BaseModel):
    """AI 解析的待办事项模型"""
    text: str = Field(description="清理后的任务文本，去除所有标识符")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="任务优先级")
    category: CategoryType = Field(default=CategoryType.DEFAULT, description="任务类别")
    deadline: Optional[str] = Field(default=None, description="截止日期，格式为 YYYY-MM-DD，如果没有明确日期则为 null")
    estimated_time: Optional[int] = Field(default=None, description="预估完成时间（分钟），如果没有提到则为 null")
    notes: Optional[str] = Field(default=None, description="额外备注信息")

class GeminiService:
    """Gemini AI 服务"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        
        if self.api_key and self.api_key != 'your_gemini_api_key_here':
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"AI 服务初始化失败: {e}")
                self.client = None
    
    def parse_todo_text(self, user_input: str) -> TodoItemAI:
        """解析用户输入的自然语言文本为结构化待办事项"""
        
        if not self.client:
            return self._basic_parse(user_input)
        
        prompt = f"""
请分析以下用户输入的待办事项文本，并提取相关信息：

用户输入："{user_input}"

请根据以下规则分析：
1. 提取核心任务文本（去除所有标识符和修饰词）
2. 识别优先级关键词：紧急、急、重要、高优先级 -> urgent；重要、高 -> high；普通、中等 -> medium；不急、低 -> low
3. 识别类别关键词：工作、项目、会议、报告 -> work；生活、购物、家务 -> life；学习、读书、课程 -> study
4. 识别时间信息：今天、明天、后天、具体日期、下周等
5. 识别预估时间：需要多长时间完成
6. 提取其他备注信息

今天的日期是：{date.today().strftime('%Y-%m-%d')}

请严格按照以下 JSON 格式返回：
{{
    "text": "清理后的任务文本",
    "priority": "low|medium|high|urgent",
    "category": "default|work|life|study",
    "deadline": "YYYY-MM-DD 或 null",
    "estimated_time": 数字或null,
    "notes": "备注信息或null"
}}

只返回 JSON，不要其他内容。
"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": TodoItemAI,
                }
            )
            
            # 直接使用解析后的对象
            if hasattr(response, 'parsed') and response.parsed:
                return response.parsed
            else:
                # 如果没有解析结果，尝试手动解析
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                result_data = json.loads(response_text)
                return TodoItemAI(**result_data)
            
        except Exception as e:
            print(f"AI 解析错误: {e}")
            # 如果 AI 解析失败，返回基本的待办事项
            return self._basic_parse(user_input)
    
    def _basic_parse(self, user_input: str) -> TodoItemAI:
        """基本解析功能，不依赖 AI"""
        # 简单的关键词匹配
        priority = PriorityLevel.MEDIUM
        category = CategoryType.DEFAULT
        
        # 优先级检测
        if any(word in user_input for word in ['紧急', '急', '重要', '高优先级']):
            priority = PriorityLevel.URGENT
        elif any(word in user_input for word in ['重要', '高']):
            priority = PriorityLevel.HIGH
        elif any(word in user_input for word in ['不急', '低']):
            priority = PriorityLevel.LOW
        
        # 类别检测
        if any(word in user_input for word in ['工作', '项目', '会议', '报告']):
            category = CategoryType.WORK
        elif any(word in user_input for word in ['生活', '购物', '家务']):
            category = CategoryType.LIFE
        elif any(word in user_input for word in ['学习', '读书', '课程']):
            category = CategoryType.STUDY
        
        return TodoItemAI(
            text=user_input,
            priority=priority,
            category=category
        )
    
    def is_available(self) -> bool:
        """检查 AI 服务是否可用"""
        return self.client is not None 