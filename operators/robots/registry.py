import importlib
import logging
import os

logger = logging.getLogger(__name__)

ROBOT_NAMES = [
    "robot_knp",
    "wb_scrapper",
]

REGISTRY = {}

for name in ROBOT_NAMES:
    try:
        module = importlib.import_module(f"robots.{name}.shell")
        REGISTRY[name] = module.run
    except Exception as e:
        logger.warning(f"Робот '{name}' не загружен: {e}")
