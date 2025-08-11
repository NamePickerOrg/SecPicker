# 示例插件

## 插件概述

这是一个简单的示例插件，用于演示 SecRandom 插件系统的基本功能和工作原理。通过此插件，开发者可以了解如何创建、配置和集成自己的插件到 SecRandom 主系统中。

## 功能特点

- **简单易用**：提供直观的图形界面和简单的API
- **配置管理**：支持插件的配置保存和加载
- **系统集成**：与 SecRandom 主系统无缝集成
- **可扩展性**：基于模块化设计，易于扩展和修改
- **完整示例**：包含插件开发的所有必要组件

## 文件结构

```
example_plugin/
├── main.py          # 插件主程序文件
├── plugin.json      # 插件配置文件
└── README.md        # 插件说明文档
```

## 安装和使用

### 1. 插件安装

将 `example_plugin` 文件夹复制到 SecRandom 的插件目录：
```
app/plugin/example_plugin/
```

### 2. 启用插件

在 SecRandom 的插件管理界面中，找到"示例插件"并启用它。

### 3. 使用插件

- 点击插件的"设置"或"打开"按钮
- 在弹出的对话框中查看插件信息
- 点击"显示信息"按钮测试插件功能

## 插件开发要点

### 1. 插件配置文件 (plugin.json)

每个插件必须包含一个 `plugin.json` 配置文件，格式如下：

```json
{
  "name": "插件名称",
  "version": "版本号",
  "description": "插件描述",
  "author": "作者",
  "entry_point": "入口文件",
  "background_service": "后台服务文件",
  "min_app_version": "最低应用版本",
  "dependencies": [],
  "enabled": true,
  "autostart": false
}
```

**配置项说明：**
- `name`: 插件显示名称
- `version`: 插件版本号（语义化版本）(格式：v1.0.0(就建议这种格式的)  或者是跟你的GitHub tag一致)
- `description`: 插件功能描述
- `author`: 插件作者
- `entry_point`: 插件入口文件（通常是 main.py）
- `background_service`: 插件后台服务文件（可选）
- `min_app_version`: 兼容的最低应用版本(格式：v0.0.0.0(必须是这个!))
- `dependencies`: 依赖列表（可选）
- `enabled`: 是否默认启用
- `autostart`: 是否自动启动(一般来说默认最好是false)

### 2. 插件主程序 (main.py)

插件主程序应包含以下核心组件：

#### A. 插件类

```python
class ExamplePlugin:
    def __init__(self):
        # 初始化插件
        pass
        
    def get_info(self) -> Dict:
        # 返回插件信息
        pass
        
    def execute(self, *args, **kwargs):
        # 执行插件主要功能
        pass
```

#### B. 界面类（可选）

```python
class ExampleDialog(QDialog):
    def __init__(self, parent=None):
        # 初始化界面
        pass
        
    def init_ui(self):
        # 设置界面组件
        pass
```

#### C. API 函数

```python
def show_dialog(parent=None):
    # 显示插件界面
    pass
    
def get_plugin_info() -> Dict:
    # 获取插件信息
    pass
    
def execute_plugin(*args, **kwargs):
    # 执行插件功能
    pass
```

### 3. 配置管理

插件应该支持配置的保存和加载：

```python
def load_config(self):
    """加载插件配置"""
    try:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        
def save_config(self):
    """保存插件配置"""
    try:
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
```

### 4. 日志记录

使用 `loguru` 库进行日志记录：

```python
from loguru import logger

logger.info("插件信息")
logger.error("错误信息")
logger.warning("警告信息")
```

### 5. 错误处理

插件应该包含完善的错误处理机制：

```python
try:
    # 可能出错的代码
    result = some_operation()
except Exception as e:
    logger.error(f"操作失败: {e}")
    # 返回错误信息或显示错误提示
```

### 6. 插件服务

如果插件需要在后台运行服务，应在 `service.py` 文件中实现：

```python
class ExampleService:
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

## 插件集成要点

### 1. 与主系统通信(暂时不支持)

插件可以通过以下方式与主系统集成：

- **信号槽机制**：使用 PyQt5 的信号槽系统
- **事件系统**：监听和响应主系统事件
- **API调用**：调用主系统提供的API接口
- **配置共享**：通过配置文件与主系统共享数据

### 2. 界面集成

- 使用 `qfluentwidgets` 保持界面风格一致
- 遵循主系统的界面设计规范
- 支持深色/浅色主题切换
- 提供合适的图标和视觉效果

### 3. 数据管理

- 使用 JSON 格式存储配置数据
- 数据文件应存储在插件目录下
- 避免直接修改主系统数据
- 提供数据备份和恢复功能

## 最佳实践

### 1. 命名规范

- 类名使用驼峰命名法（如 `ExamplePlugin`）
- 函数名使用下划线命名法（如 `show_dialog`）
- 常量使用大写字母（如 `MAX_COUNT`）
- 文件名使用小写字母和下划线（如 `main.py`）

### 2. 代码组织

- 将相关功能组织在同一个类中
- 使用清晰的注释说明代码功能
- 避免过长的函数，适当拆分复杂逻辑
- 保持代码的可读性和可维护性

### 3. 性能优化

- 避免在插件中进行耗时操作
- 使用异步处理长时间任务
- 合理使用缓存机制
- 及时释放不再使用的资源

### 4. 兼容性考虑

- 检查主系统版本兼容性
- 处理不同操作系统的差异
- 提供降级方案处理异常情况
- 避免使用过于新的Python特性

## 调试和测试

### 1. 调试方法

```python
# 在 main.py 末尾添加测试代码
if __name__ == "__main__":
    app = QApplication([])
    dialog = ExampleDialog()
    dialog.show()
    app.exec_()
```

### 2. 常见问题

- **导入失败**：检查依赖库是否正确安装
- **界面不显示**：检查 PyQt5 和 qfluentwidgets 是否正常工作
- **配置无法保存**：检查文件权限和路径是否正确
- **插件无法加载**：检查 plugin.json 格式是否正确

## 扩展建议

基于此示例插件，您可以开发以下类型的扩展：

1. **功能增强插件**：扩展主系统的核心功能
2. **界面美化插件**：提供自定义主题和样式
3. **数据导入导出插件**：支持更多数据格式
4. **自动化插件**：实现自动化的操作流程
5. **集成插件**：与其他系统或服务集成

## 技术支持

如果在插件开发过程中遇到问题，请参考以下资源：

- SecRandom 主系统文档
- PyQt5 官方文档
- qfluentwidgets 项目文档
- loguru 日志库文档

---

© 2025 SecRandom Team. All rights reserved.