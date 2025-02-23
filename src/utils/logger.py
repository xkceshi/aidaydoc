import logging
import os
from datetime import datetime

def setup_logger():
    logger = logging.getLogger('daydoc')
    logger.setLevel(logging.INFO)  # 将日志级别改为 INFO
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 处理器也设置为 DEBUG
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # 确保不会重复添加处理器
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger
    # 创建 logs 目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志文件名（按日期）
    log_file = os.path.join(log_dir, f'daydoc_{datetime.now().strftime("%Y%m%d")}.log')

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )

    return logging.getLogger('daydoc')