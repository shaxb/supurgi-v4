from loguru import logger
import os

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Custom log format with colors for console
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<cyan>{file}:{line}</cyan> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)

# Configure loguru for file (no colors) and console (with colors)
LOG_FILE_PATH = os.path.join(LOG_DIR, "report.log")
logger.remove()  # Remove default handler

logger.add(
    LOG_FILE_PATH,
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {file}:{line} | {level: <8} | {message}",
    colorize=False
)
logger.add(
    lambda msg: print(msg, end=""),
    format=LOG_FORMAT,
    colorize=True
)

logger.info("Custom logging initialized.")

# Usage in other modules:
# from services.market_data.custom_logging import logger
# logger.info("Your log message here")