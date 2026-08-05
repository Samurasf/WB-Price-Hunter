import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "wb_price_hunter.log"

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8"
)

console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger("WB_PRICE_HUNTER")
logger.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(console_handler)