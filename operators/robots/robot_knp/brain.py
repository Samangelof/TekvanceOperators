import os
import time
from common.logger import get_logger
from operators.robots.robot_knp.driver import KnpDriver


logger = get_logger("robot_knp")


class KnpController:
    def __init__(self, config: dict):
        self.driver = KnpDriver(config)
    
    def run(self): 
        try:
            self.driver.open_homepage()
            self.driver.wait_for_load()
            self.driver.switch_language_to_russian()
            self.driver.login_by_cert()

            base_folder = self.driver.config.get("eds_folder", "")
            for subdir in os.listdir(base_folder):
                full_path = os.path.join(base_folder, subdir)
                if not os.path.isdir(full_path):
                    continue

                if self.driver.select_cert_from_dir(full_path):
                    logger.info(f"[FLOW] Вошли с сертификатом: {full_path}")
                    
                    # ==== логика между входом и выходом ====
                    self.process_session_workflow(full_path)
                    # ============================================

                    self.driver.logout()

            logger.info(f"Title: {self.driver.driver.title}")

        except Exception as e:
            logger.error(f"Ошибка в run(): {e}")
            raise
    
    def process_session_workflow(self, cert_path: str):
        """Шаги сценария между входом и выходом."""
        logger.info(f"[SESSION] Старт задач для {cert_path}")
        time.sleep(2)
        logger.info(f"[SESSION] Сделано 1/2 действие для {cert_path}")
        time.sleep(2)
        logger.info(f"[SESSION] Сделано 2/2 действие для {cert_path}")



    def close(self):
        if getattr(self.driver, "driver", None):
            self.driver.driver.quit()
            logger.info("Драйвер закрыт")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()