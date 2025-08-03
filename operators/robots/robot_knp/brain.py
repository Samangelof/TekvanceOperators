from common.logger import get_logger
from operators.robots.robot_knp.driver import RobotKnpDriver


logger = get_logger("robot_knp")


class KnpRobot:
    def __init__(self, config: dict):
        self.driver = RobotKnpDriver(config)
    
    def run(self):
        try:
            self.driver.open_homepage()
            self.driver.wait_for_load()
            self.driver.switch_language_to_russian()
            self.driver.login_by_cert()
            self.driver.select_cert_from_dir(self.driver.config.get("eds_folder", ""))

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