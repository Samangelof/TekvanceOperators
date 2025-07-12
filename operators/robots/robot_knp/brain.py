# robots/robot_knp/brain.py
from robots.base.base_selenium import BaseSeleniumRobot
from common.logger import get_logger


logger = get_logger("robot_knp")

class KnpRobot(BaseSeleniumRobot):
    def run(self):
        self.driver.get("https://example.com")
        title = self.driver.title
        logger.info(f"[KnpRobot] Title: {title}")
        # дальше — нужный парсинг, клик, извлечение
