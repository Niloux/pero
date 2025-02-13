import copy
import json
import logging
import logging.handlers
import sys
import threading
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Union


class LogFormatter(logging.Formatter):
    """自定义日志格式化器，支持彩色输出和JSON格式"""

    COLORS = {
        "DEBUG": "\033[94m",  # 蓝色
        "INFO": "\033[92m",  # 绿色
        "WARNING": "\033[93m",  # 黄色
        "ERROR": "\033[91m",  # 红色
        "CRITICAL": "\033[95m",  # 紫色
        "TIME": "\033[96m",  # 青色
        "THREAD": "\033[90m",  # 灰色
        "ENDC": "\033[0m",  # 结束符
    }

    def __init__(self, use_color: bool = True, json_format: bool = False):
        super().__init__()
        self.use_color = use_color
        self.json_format = json_format

    def format(self, record: logging.LogRecord) -> str:
        # 创建一个副本以避免修改原始记录
        record_copy = copy.copy(record)

        # 添加线程ID
        record_copy.thread_name = threading.current_thread().name

        # 格式化异常信息
        if record_copy.exc_info:
            record_copy.exc_text = "".join(
                traceback.format_exception(*record_copy.exc_info)
            )

        if self.json_format:
            log_data = {
                "timestamp": datetime.fromtimestamp(record_copy.created).isoformat(),
                "level": record_copy.levelname,
                "logger": record_copy.name,
                "thread": record_copy.thread_name,
                "message": record_copy.getMessage(),
                "module": record_copy.module,
                "func": record_copy.funcName,
                "line": record_copy.lineno,
            }

            if hasattr(record_copy, "extra_data"):
                log_data["extra_data"] = record_copy.extra_data

            if record_copy.exc_text:
                log_data["exception"] = record_copy.exc_text

            return json.dumps(log_data)
        else:
            # 标准格式输出
            log_msg = ""

            if self.use_color:
                log_msg += f"{self.COLORS['TIME']}"
            log_msg += f"[{datetime.fromtimestamp(record_copy.created).isoformat()}] "
            if self.use_color:
                log_msg += f"{self.COLORS['ENDC']}"

            if self.use_color:
                log_msg += f"{self.COLORS['THREAD']}"
            log_msg += f"[{record_copy.thread_name}] "
            if self.use_color:
                log_msg += f"{self.COLORS['ENDC']}"

            if self.use_color:
                log_msg += f"{self.COLORS.get(record_copy.levelname, '')}"

            log_msg += f"[{record_copy.levelname}] "
            log_msg += f"[{record_copy.name}] "
            log_msg += (
                f"[{record_copy.module}.{record_copy.funcName}:{record_copy.lineno}] "
            )
            log_msg += f"{record_copy.getMessage()}"

            if self.use_color:
                log_msg += self.COLORS["ENDC"]

            if hasattr(record_copy, "extra_data"):
                log_msg += (
                    f"\nExtra Data: {json.dumps(record_copy.extra_data, indent=2)}"
                )

            if record_copy.exc_text:
                log_msg += f"\nException:\n{record_copy.exc_text}"

            return log_msg


class EnhancedLogger:
    """增强的日志记录器，提供更多功能和更好的使用体验"""

    def __init__(
        self,
        name: str,
        log_dir: Union[str, Path] = "logs",
        log_level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
        use_color: bool = True,
        json_format: bool = False,
    ):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # 创建日志目录
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志文件处理器
        log_file = log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(
            LogFormatter(use_color=False, json_format=json_format)
        )
        self.logger.addHandler(file_handler)

        # 设置控制台输出
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                LogFormatter(use_color=use_color, json_format=json_format)
            )
            self.logger.addHandler(console_handler)

        # 错误日志单独存储
        error_file = log_dir / f"{name}_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            filename=str(error_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            LogFormatter(use_color=False, json_format=json_format)
        )
        self.logger.addHandler(error_handler)

    def _log(
        self,
        level: int,
        msg: str,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info=None,
    ):
        """统一的日志记录方法"""
        extra = {}
        if extra_data:
            extra["extra_data"] = extra_data
        self.logger.log(level, msg, extra=extra, exc_info=exc_info, stacklevel=3)

    def debug(self, msg: str, extra_data: Optional[Dict[str, Any]] = None):
        self._log(logging.DEBUG, msg, extra_data)

    def info(self, msg: str, extra_data: Optional[Dict[str, Any]] = None):
        self._log(logging.INFO, msg, extra_data)

    def warning(self, msg: str, extra_data: Optional[Dict[str, Any]] = None):
        self._log(logging.WARNING, msg, extra_data)

    def error(
        self, msg: str, extra_data: Optional[Dict[str, Any]] = None, exc_info=True
    ):
        self._log(logging.ERROR, msg, extra_data, exc_info)

    def critical(
        self, msg: str, extra_data: Optional[Dict[str, Any]] = None, exc_info=True
    ):
        self._log(logging.CRITICAL, msg, extra_data, exc_info)

    @staticmethod
    def log_execution_time(logger_instance: "EnhancedLogger"):
        """方法执行时间装饰器"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = datetime.now()
                try:
                    result = func(*args, **kwargs)
                    end_time = datetime.now()
                    execution_time = (end_time - start_time).total_seconds()
                    logger_instance.info(
                        f"Function '{func.__name__}' executed in {execution_time:.3f} seconds",
                        extra_data={"execution_time": execution_time},
                    )
                    return result
                except Exception as e:
                    end_time = datetime.now()
                    execution_time = (end_time - start_time).total_seconds()
                    logger_instance.error(
                        f"Error in function '{func.__name__}'",
                        extra_data={"execution_time": execution_time, "error": str(e)},
                    )
                    raise

            return wrapper

        return decorator


logger = EnhancedLogger(
    name="pero",
    log_level=logging.DEBUG,
    console_output=True,
    use_color=True,
    json_format=False,
)

# 使用示例
if __name__ == "__main__":
    # 基本日志记录
    logger.debug("This is a debug message")
    logger.info("This is an info message", extra_data={"user_id": 123})
    logger.warning("This is a warning message")

    # 记录异常
    try:
        1 / 0
    except Exception:
        logger.error("An error occurred", extra_data={"operation": "division"})

    # 使用装饰器记录执行时间
    @logger.log_execution_time(logger)
    def slow_operation():
        import time

        time.sleep(1)
        return "Operation completed"

    slow_operation()
