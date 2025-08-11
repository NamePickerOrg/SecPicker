# SecRandom 插件系统

## 概述

SecRandom 插件系统为应用程序提供了灵活的扩展机制。通过插件系统，开发者可以轻松地添加新功能、扩展现有功能，并与主系统深度集成。

## 插件目录结构

```
app/plugin/
├── example_plugin/          # 示例插件
│   ├── plugin.json         # 插件配置文件
│   ├── main.py            # 插件主程序
│   └── README.md          # 插件说明文档
└── [其他插件]/            # 其他插件目录
    ├── plugin.json
    ├── main.py
    └── README.md
```

## 建议

- **插件开发建议使用SecRandom已有的内置库,这样不用安装额外的库,也不会产生更复杂的教程**
- **插件开发建议使用开发SecRandom的Python版本(或更高版本),这样可以避免版本冲突**
- **插件开发建议使用SecRandom的日志库(loguru),这样可以方便地记录插件运行日志(建议存储在你自己插件目录下的log文件中)**
- **插件开发建议使用SecRandom的配置库(json),这样可以方便地读取插件配置文件(建议存储在你自己插件目录下的config文件中)**

## 插件开发要点

### 1. 必需文件

每个插件必须包含以下文件：

- **plugin.json**: 插件配置文件，定义插件的基本信息
- **main.py**: 插件主程序，包含插件的核心功能
- **README.md**: 插件说明文档，提供使用指南

### 2. 插件配置文件 (plugin.json)

```json
{
  "name": "插件名称",
  "version": "1.0.0",
  "description": "插件功能描述",
  "author": "插件作者",
  "entry_point": "main.py",
  "background_service": "service.py",
  "min_app_version": "1.0.0.0",
  "dependencies": [],
  "enabled": true,
  "autostart": false
}
```

### 3. 插件主程序 (main.py)

```python
# 导入必要的库
import json
import os
from typing import Dict, List, Optional
from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from loguru import logger

# 插件类
class MyPlugin:
    def __init__(self):
        self.config_path = "app/plugin/my_plugin/config.json"
        self.config = {}
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            
    def get_info(self) -> Dict:
        """获取插件信息"""
        return {
            "name": "我的插件",
            "version": "1.0.0",
            "description": "插件描述"
        }
        
    def execute(self, *args, **kwargs):
        """执行插件功能"""
        return "插件执行成功"

# API 函数
def show_dialog(parent=None):
    """显示插件界面"""
    dialog = __MyPluginDialog(parent) # 例子
    dialog.exec_()
    
def get_plugin_info() -> Dict:
    """获取插件信息"""
    plugin = MyPlugin()
    return plugin.get_info()
```

### 4. 插件服务

如果插件需要在后台运行服务，应在 `service.py` 文件中实现：

```python
class MyPluginService:
    def __init__(self):
        # 初始化服务
        pass
        
    def start(self):
        # 启动服务
        pass
        
    def stop(self):
        # 停止服务
        pass
```

## 插件系统特性

### 核心优势

1. **模块化设计**: 每个插件都是独立的模块，便于开发和维护
2. **易于集成**: 提供标准的API接口，与主系统无缝集成
3. **配置灵活**: 支持动态配置，用户可以自定义插件行为
4. **界面统一**: 使用 qfluentwidgets 保持界面风格一致
5. **错误处理**: 完善的异常处理和日志记录机制

### 技术特点

- **基于 PyQt5**: 使用成熟的桌面应用框架
- **配置管理**: JSON 格式的配置文件，易于编辑和备份
- **日志系统**: 集成 loguru 日志库，便于调试和监控
- **信号槽机制**: 支持事件驱动的编程模式
- **类型提示**: 使用 Python 类型提示，提高代码质量

## 开发指南

### 1. 环境要求

- Python 3.8.10+
- PyQt5
- qfluentwidgets
- loguru

### 2. 开发步骤

1. **创建插件目录**: 在 `app/plugin/` 下创建插件目录
2. **编写配置文件**: 创建 `plugin.json` 定义插件信息
3. **实现主程序**: 编写 `main.py` 实现插件功能
4. **实现服务**: 如果需要后台服务，编写 `service.py`
5. **添加界面**: 创建图形界面（如需要）
6. **编写文档**: 创建 `README.md` 说明插件用法
7. **测试调试**: 测试插件功能并调试问题
8. **打包发布**: 打包插件为 zip 文件，发布到插件广场

### 3. 最佳实践

- **命名规范**: 使用清晰的命名约定
- **错误处理**: 添加适当的异常处理
- **日志记录**: 记录重要的操作和错误
- **配置管理**: 合理使用配置文件
- **界面设计**: 遵循主系统的界面风格

### 4. 调试技巧

```python
# 在 main.py 末尾添加测试代码
if __name__ == "__main__":
    app = QApplication([])
    # 测试插件功能
    dialog = MyDialog()
    dialog.show()
    app.exec_()
```

### 5. 软件没有对应库的情况

在插件系统中，如果软件没有对应库的情况，需要在插件的 `plugin.json` 文件中添加 `dependencies` 字段，指定插件依赖的库。例如：

```json
{
  "name": "插件名称",
  "version": "1.0.0",
  "description": "插件功能描述",
  "author": "插件作者",
  "entry_point": "main.py",
  "min_app_version": "1.0.0",
  "dependencies": ["transformers", "torch"],
  "enabled": true
}
```

### 6. SecRandom 程序逻辑是怎么安装python库的？

SecRandom 程序在启动时会检查插件目录下的 `plugin.json` 文件，根据 `dependencies` 字段安装插件依赖的库。如果库不存在，程序会自动从 PyPI 下载并安装。

### 7. 插件的依赖库是怎么管理的？

插件的依赖库会被安装到 SecRandom 程序插件目录下的 `site-packages` 目录下。每个插件的依赖库都是独立的，不会与其它插件的库冲突。

## 现有插件

### 1. 示例插件 (example_plugin)
- **功能**: 演示插件系统的基本功能
- **位置**: `app/plugin/example_plugin/`
- **用途**: 提供插件开发的示例

## 常见问题

### Q: 如何创建一个新的插件？
A: 复制 `example_plugin` 目录，修改其中的文件来实现你的功能。

### Q: 插件如何与主系统通信？
A: 可以通过信号槽、事件系统或直接调用主系统API来实现通信。

### Q: 如何处理插件的配置？
A: 使用 JSON 格式的配置文件，在插件初始化时加载，修改时保存。

### Q: 插件的界面如何保持一致？
A: 使用 qfluentwidgets 库创建界面，遵循主系统的设计规范。

---

© 2025 SecRandom. All rights reserved.