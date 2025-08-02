from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import time

from common.logger import get_logger
from robots.base.base import BaseRobot


logger = get_logger("core_knp")

class BaseSeleniumRobot(BaseRobot):
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.config = config or {}
        self.driver = self._init_driver()
        print(f"[DEBUG] driver config: {self.config}")


    def open_homepage(self):
        url = self.config["start_url"]
        self.driver.get(url)
        self.wait_for_load()

    
    def wait_for_load(self):
        """Ожидание полной загрузки с проверкой состояния"""
        from selenium.webdriver.support.ui import WebDriverWait
        
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        try:
            wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, ".loading, .spinner, [data-loading]")))
        except:
            pass
        
    def switch_language_to_russian(self):
        """Сменить язык интерфейса на русский"""
        try:
            wait = WebDriverWait(self.driver, 60)
            lang_elem = wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'lang-switcher')]//a[text()='Русский']"
            )))
            lang_elem.click()
            time.sleep(10)
        except TimeoutException:
            logger.warning("Элемент 'Русский' не появился.")
        except Exception as e:
            logger.error(f"Ошибка при смене языка: {e}", exc_info=True)

    def close(self):
        if getattr(self, "driver", None):
            self.driver.quit()

    def __del__(self):
        self.close()
