from loguru import logger
import os
import sys
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger.remove()
logger.add(sys.stdout, level="INFO")

def _log_path(name: str):
    date = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{name}_{date}.log")

class ChannelFilter:
    def __init__(self, channel_name):
        self.channel = channel_name

    def __call__(self, record):
        return record["extra"].get("channel") == self.channel

_initialized_channels = set()

def get_logger(channel: str):
    if channel not in _initialized_channels:
        path = _log_path(channel)
        logger.add(path, level="DEBUG", rotation="1 MB", filter=ChannelFilter(channel))
        _initialized_channels.add(channel)
    return logger.bind(channel=channel)
