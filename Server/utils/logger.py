import logging
from datetime import datetime
import os

# 日志文件路径（项目目录内）
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs')
os.makedirs(LOG_DIR, exist_ok=True)  # 确保日志目录存在
LOG_FILE = os.path.join(LOG_DIR, 'application.log')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 控制台日志
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")  # 文件日志
    ]
)

# 日志记录函数
def log_message(message, level="info"):
    """记录日志到控制台和文件"""
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
