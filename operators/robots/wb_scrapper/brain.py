# Логика сценария для wb_scrapper
from common.logger import get_logger
from operators.robots.wb_scrapper.driver import RobotWbDriver


logger = get_logger("wb_scrapper")


class WbRobot:
    def __init__(self, config: dict):
        self.driver = RobotWbDriver(config)
    
    def run(self):
        try:
            self.driver.open_homepage()
            self.driver.wait_for_load()
            logger.info(f"Title: {self.driver.driver.title}")
        except Exception as e:
            logger.error(f"Ошибка в run(): {e}")
            raise
    
    def close(self):
        """Закрыть драйвер"""
        if hasattr(self.driver, 'driver') and self.driver.driver:
            self.driver.driver.quit()
            logger.info("Драйвер закрыт")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()