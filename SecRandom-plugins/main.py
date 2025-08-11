import json
import os
from typing import Dict, List, Optional
from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from loguru import logger

class ExampleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("示例插件")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 标题标签
        title_label = BodyLabel("欢迎使用示例插件！")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        
        # 内容文本
        content_text = TextEdit()
        content_text.setReadOnly(True)
        content_text.setPlainText(
            "这是一个简单的示例插件，用于演示 SecRandom 插件系统的基本功能。\n\n"
            "功能特点：\n"
            "• 简单的图形界面\n"
            "• 基本的配置管理\n"
            "• 与主系统集成\n"
            "• 可扩展的架构\n\n"
            "您可以通过修改此插件来创建自己的功能扩展。"
        )
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.show_info_btn = PushButton("显示信息")
        self.show_info_btn.clicked.connect(self.show_info)
        
        self.close_btn = PushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.show_info_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addWidget(title_label)
        layout.addWidget(content_text)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def show_info(self):
        """显示插件信息"""
        InfoBar.info(
            title="插件信息",
            content="示例插件运行正常！",
            orient=Qt.Horizontal,
            parent=self,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP
        )


class ExamplePlugin:
    """示例插件主类"""
    
    def __init__(self):
        self.config_path = "app/plugin/example_plugin/config.json"
        self.config = {}
        self.load_config()
        
    def load_config(self):
        """加载插件配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "enabled": True,
                    "show_welcome": True,
                    "custom_message": "欢迎使用示例插件！"
                }
                self.save_config()
        except Exception as e:
            logger.error(f"加载插件配置失败: {e}")
            self.config = {}
            
    def save_config(self):
        """保存插件配置"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存插件配置失败: {e}")
            
    def get_info(self) -> Dict:
        """获取插件信息"""
        return {
            "name": "示例插件",
            "version": "1.0.0",
            "description": "这是一个简单的示例插件",
            "author": "SecRandom Team",
            "enabled": self.config.get("enabled", True)
        }
        
    def execute(self, *args, **kwargs):
        """执行插件主要功能"""
        logger.info("示例插件被执行")
        return "示例插件执行成功"


# 插件API函数
def show_dialog(parent=None):
    """显示示例插件对话框"""
    dialog = ExampleDialog(parent)
    dialog.exec_()
    
def get_plugin_info() -> Dict:
    """获取插件信息"""
    plugin = ExamplePlugin()
    return plugin.get_info()
    
def execute_plugin(*args, **kwargs):
    """执行插件功能"""
    plugin = ExamplePlugin()
    return plugin.execute(*args, **kwargs)


# 插件入口点
if __name__ == "__main__":
    # 测试插件功能
    app = QApplication([])
    dialog = ExampleDialog()
    dialog.show()
    app.exec_()