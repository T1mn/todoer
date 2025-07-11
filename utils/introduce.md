# Utils 模块功能概述

此目录包含应用程序的各种工具模块，提供数据转换、AI 解析和其他辅助功能。

## 文件列表及功能

### `data_converter.py`
- **功能**：数据转换工具，处理文本到日期和优先级的转换
- **核心类**：`DataConverter`
- **主要方法**：
  - `convert_text_to_date()`: 解析文本中的日期信息
  - `convert_text_to_priority()`: 解析文本中的优先级信息
- **支持格式**：
  - 日期：今天、明天、后天、具体日期格式
  - 优先级：#紧急、#urgent、#重要、#high 等标识符

### `ai_service.py` ⭐ 新增
- **功能**：Gemini AI 智能解析服务
- **核心类**：
  - `GeminiService`: AI 服务主类
  - `TodoItemAI`: AI 解析结果数据模型（使用 Pydantic）
  - `PriorityLevel`: 优先级枚举
  - `CategoryType`: 类别枚举
- **主要功能**：
  - 自然语言文本解析
  - 结构化数据提取（使用 Gemini 结构化输出）
  - 智能优先级和类别识别
  - 时间信息解析
  - 错误处理和回退机制
- **技术特点**：
  - 使用标准的 `from google import genai` 导入
  - 支持 Pydantic 模型验证
  - 使用 Gemini 1.5 Flash 模型
  - 自动 JSON 解析和对象转换

### `ai_converter.py` ⭐ 新增
- **功能**：AI 数据转换器
- **核心类**：`AIConverter`
- **主要方法**：
  - `convert_ai_to_todo_item()`: 将 AI 解析结果转换为应用程序的 TodoItem 格式
- **转换映射**：
  - 优先级映射：AI 枚举 → 应用程序枚举
  - 类别映射：AI 分类 → 应用程序分类
  - 日期转换：字符串日期 → QDate 对象

## 相互关系

### 数据流向
```
用户输入 → AI Service → AI Converter → Todo Model
    ↓
普通解析 → Data Converter → Todo Model
```

### 依赖关系
- `ai_service.py` 依赖：
  - `google.genai`: Google Gemini API 客户端（标准导入）
  - `pydantic`: 数据验证和模型定义
  - `python-dotenv`: 环境变量管理
- `ai_converter.py` 依赖：
  - `ai_service.py`: AI 数据模型
  - `model.todo_model`: 应用程序数据模型
- `data_converter.py` 依赖：
  - `PyQt5.QtCore`: QDate 对象

### 功能互补
- **AI 解析**：处理自然语言输入，提供智能化的数据提取
- **传统解析**：处理结构化输入，提供基础的模式匹配
- **数据转换**：统一不同来源的数据格式，确保数据一致性

## 外部关系

### 与 Controller 的关系
- `AppController` 集成 `GeminiService` 和 `AIConverter`
- 通过 `ai_parse_item()` 方法处理 AI 解析请求
- 提供错误处理和回退机制

### 与 Model 的关系
- 所有转换器最终都生成 `TodoItem` 对象
- 确保数据格式与模型要求一致

### 与 View 的关系
- 通过 `Shift+Enter` 快捷键触发 AI 解析
- 用户界面保持简洁，AI 功能透明集成

## 配置要求

### 环境变量
- `GEMINI_API_KEY`: Google Gemini API 密钥（必需）

### 依赖包
- `google-generativeai`: AI 服务核心依赖
- `pydantic`: 数据验证和序列化
- `python-dotenv`: 环境变量管理

## 使用方式

### AI 解析模式
1. 用户输入自然语言描述
2. 按 `Shift+Enter` 触发 AI 解析
3. `GeminiService` 处理文本并返回结构化数据
4. `AIConverter` 转换数据格式
5. 添加到待办事项列表

### 传统解析模式
1. 用户输入结构化文本（包含标识符）
2. 按 `Enter` 触发普通解析
3. `DataConverter` 解析文本模式
4. 直接添加到待办事项列表

## 错误处理

### AI 服务不可用
- 自动回退到基本关键词匹配
- 保持应用程序正常运行
- 输出相关日志信息

### 网络问题
- 超时处理
- 重试机制
- 优雅降级到传统解析

### 数据格式错误
- JSON 解析错误处理
- 数据验证失败处理
- 默认值填充机制 