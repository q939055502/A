
"""日志处理工具模块"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import current_app

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 日志文件名格式
log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')

# 创建日志记录器
logger = logging.getLogger('app')

# 创建控制台处理器
console_handler = logging.StreamHandler()
# 默认控制台只输出WARNING及以上级别的日志
console_handler.setLevel(logging.WARNING)

# 创建文件处理器 (带有轮转功能)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=1024 * 1024 * 10,  # 10MB
    backupCount=5,  # 保留5个备份文件
    encoding='utf-8'
)

# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)
# 默认日志级别
logger.setLevel(logging.INFO)


def setup_logger(app=None):
    """
    根据应用配置设置日志级别
    应在应用初始化后调用此函数
    
    Args:
        app: Flask应用实例，如果未提供则尝试使用current_app
    """
    # 默认日志级别
    default_level = logging.INFO
    
    try:
        # 获取应用实例
        current_app = app or current_app
        
        # 从配置中获取日志级别
        log_level = current_app.config.get('LOG_LEVEL', 'INFO').upper()
        
        # 转换为logging模块的级别常量
        level = getattr(logging, log_level, default_level)
        
        # 设置日志级别
        logger.setLevel(level)
        # 控制台只输出WARNING及以上级别的日志
        console_handler.setLevel(logging.WARNING)
        file_handler.setLevel(level)
        
        logger.info(f"日志级别已设置为: {log_level}")
    except Exception as e:
        # 避免递归错误，直接打印到控制台
        print(f"设置日志级别失败: {str(e)}")
        # 使用默认级别
        logger.setLevel(default_level)
        console_handler.setLevel(default_level)
        file_handler.setLevel(default_level)

# 测试日志
# logger.info('日志系统初始化完成')
