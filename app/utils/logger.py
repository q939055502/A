
"""日志处理工具模块"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 日志文件名格式
log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')

# 创建日志记录器
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)  # 设置默认日志级别

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建文件处理器 (带有轮转功能)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=1024 * 1024 * 10,  # 10MB
    backupCount=5,  # 保留5个备份文件
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)

# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 测试日志
# logger.info('日志系统初始化完成')
