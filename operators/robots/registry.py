from pathlib import Path
import importlib
import logging


logger = logging.getLogger(__name__)

ROBOT_ROOT = Path(__file__).parent
REGISTRY = {}

for robot_dir in ROBOT_ROOT.iterdir():
    if not robot_dir.is_dir():
        continue
    if (robot_dir / "shell.py").exists():
        name = robot_dir.name
        try:
            module = importlib.import_module(f"robots.{name}.shell")
            REGISTRY[name] = module.run
        except Exception as e:
            logger.warning(f"Робот '{name}' не загружен: {e}")
