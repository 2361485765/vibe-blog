"""
日志配置模块
从 app.py 抽取的日志初始化逻辑
"""
import os
import logging
from contextvars import ContextVar

# 创建任务 ID 上下文变量
task_id_context: ContextVar[str] = ContextVar('task_id', default='')


class TaskIdFilter(logging.Filter):
    """自定义日志过滤器，添加任务 ID"""
    def filter(self, record):
        task_id = task_id_context.get()
        if task_id:
            record.task_id = f"[{task_id}]"
        else:
            record.task_id = ""
        return True


def setup_logging():
    """配置日志系统"""
    log_format = logging.Formatter('%(asctime)s %(task_id)s - %(name)s - %(levelname)s - %(message)s')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    task_id_filter = TaskIdFilter()
    root_logger.addFilter(task_id_filter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    console_handler.addFilter(task_id_filter)
    root_logger.addHandler(console_handler)

    # 尝试配置文件日志，如果失败则跳过（Vercel 环境是只读的）
    try:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        file_handler.addFilter(task_id_filter)
        root_logger.addHandler(file_handler)
        logger_init = logging.getLogger(__name__)
        logger_init.info("✅ 日志文件已启用，DEBUG 级别日志将写入文件")
    except (OSError, IOError):
        pass
