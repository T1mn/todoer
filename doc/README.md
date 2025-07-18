# Doc 模块

此模块包含项目的文档资源、演示材料和多媒体内容，为用户和开发者提供可视化的使用指导。

## 功能概述

- **用户指南**: 提供应用程序的使用演示和教程
- **开发文档**: 包含项目的技术文档和API说明
- **媒体资源**: 存储截图、动画和演示视频
- **示例材料**: 展示应用程序功能的实际案例

## 文件列表

### `todoer.gif`
- **功能**: 应用程序主要功能的动态演示
- **内容**:
  - 添加和管理待办事项的操作流程
  - 番茄钟计时器的使用方式
  - AI解析功能的演示
  - 云同步操作的展示
- **用途**:
  - README.md中的功能展示
  - 用户手册的配图
  - 项目演示和宣传

## 资源规范

### 图像要求
- **格式**: GIF、PNG、JPG
- **尺寸**: 适合网页显示（宽度不超过800px）
- **质量**: 清晰度足够展示界面细节
- **大小**: 单文件不超过5MB，确保加载速度

### 视频要求
- **格式**: MP4、GIF（短片段）
- **时长**: 30秒以内的功能演示
- **分辨率**: 1080p或适合的显示分辨率
- **帧率**: 15-30fps，确保流畅播放

## 使用方式

### 在文档中引用
```markdown
# 功能演示
![应用程序演示](doc/todoer.gif)

# 截图展示
![主界面](doc/screenshots/main-window.png)
```

### 生成新的演示材料
```bash
# 录制屏幕演示（Linux）
ffmpeg -video_size 1920x1080 -framerate 25 -f x11grab -i :0.0 output.mp4

# 转换为GIF
ffmpeg -i output.mp4 -vf "scale=800:-1" -r 10 todoer.gif
```

## 内容分类

### 功能演示
- 核心功能的操作流程
- 用户界面的交互方式
- 特色功能的使用方法

### 界面截图
- 主窗口和对话框
- 不同主题的外观
- 各种状态下的界面

### 技术图表
- 系统架构图
- 数据流程图
- 组件关系图

## 制作指南

### 演示录制建议
1. **准备工作**:
   - 清理桌面环境
   - 设置合适的窗口大小
   - 准备演示数据

2. **录制过程**:
   - 突出关键操作步骤
   - 保持操作节奏适中
   - 展示结果和反馈

3. **后期处理**:
   - 裁剪无关内容
   - 调整播放速度
   - 添加必要的说明

### 文档配图原则
- **清晰性**: 图像清晰，文字可读
- **相关性**: 图像内容与文档主题相关
- **一致性**: 风格和格式保持统一
- **时效性**: 确保图像反映最新版本

## 维护更新

### 定期更新
- 主要功能变更时更新演示
- 界面改版时更新截图
- 新功能发布时添加文档

### 版本管理
- 为不同版本保留对应的文档
- 使用版本号标识文档内容
- 清理过期的演示材料

## 依赖关系

### 内容来源
- `view/`: 界面截图和演示录制
- `main.py`: 应用程序运行演示
- 功能模块: 各种功能的使用演示

### 使用场景
- `README.md`: 项目介绍和演示
- 用户手册: 操作指导配图
- 开发文档: 技术说明图表

## 工具推荐

### 录制工具
- **Linux**: SimpleScreenRecorder, OBS Studio
- **Windows**: OBS Studio, Bandicam
- **macOS**: QuickTime Player, ScreenFlow

### 编辑工具
- **图像编辑**: GIMP, Photoshop
- **GIF制作**: GIMP, FFmpeg
- **视频编辑**: DaVinci Resolve, FFmpeg

## 存储优化

- 使用适当的压缩比例
- 定期清理临时文件
- 考虑使用CDN存储大文件
- 为移动设备提供优化版本 