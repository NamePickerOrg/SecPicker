import os
import sys
import time
import threading
import subprocess
from loguru import logger

class BackgroundService:
    def __init__(self, plugin_path):
        self.plugin_path = plugin_path
        self.running = False
        self.thread = None
        
    def start(self):
        """启动后台服务"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_service, daemon=True)
        self.thread.start()
        logger.info(f"插件 {os.path.basename(self.plugin_path)} 后台服务已启动")
    
    def stop(self):
        """停止后台服务"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        logger.info(f"插件 {os.path.basename(self.plugin_path)} 后台服务已停止")
    
    def _run_service(self):
        """运行后台服务主循环"""
        logger.info(f"插件 {os.path.basename(self.plugin_path)} 后台服务开始运行")
        
        try:
            # 这里可以添加插件特定的后台逻辑
            # 例如：定时任务、监听事件、数据处理等
            while self.running:
                # 示例：每60秒执行一次任务
                time.sleep(60)
                
                # 在这里添加插件的后台逻辑
                self._execute_background_task()
                
        except Exception as e:
            logger.error(f"插件 {os.path.basename(self.plugin_path)} 后台服务运行错误: {e}")
    
    def _execute_background_task(self):
        """执行后台任务（可由插件开发者重写此方法）"""
        # 默认实现：记录日志
        logger.info(f"插件 {os.path.basename(self.plugin_path)} 后台任务执行中...")
        
        # 插件开发者可以在这里添加自己的后台逻辑
        # 例如：
        # - 数据同步
        # - 定时检查
        # - 消息推送
        # - 系统监控
        # 等等

# 全局服务实例
service_instance = None

def start_background_service(plugin_path):
    """启动后台服务"""
    global service_instance
    if service_instance is None:
        service_instance = BackgroundService(plugin_path)
        service_instance.start()
    return service_instance

def stop_background_service():
    """停止后台服务"""
    global service_instance
    if service_instance:
        service_instance.stop()
        service_instance = None

if __name__ == "__main__":
    # 当作为独立脚本运行时的测试代码
    plugin_path = os.path.dirname(os.path.abspath(__file__))
    service = start_background_service(plugin_path)
    
    try:
        # 保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_background_service()