import logging
from pythonjsonlogger import jsonlogger
import os

def setup_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Ensure log directory exists
        log_dir = os.getenv('LOG_DIR', '/app/logs')
        os.makedirs(log_dir, exist_ok=True)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(f"{log_dir}/{service_name}.log")
        file_handler.setLevel(logging.INFO)

        # JSON formatter
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(request_id)s %(user_id)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger