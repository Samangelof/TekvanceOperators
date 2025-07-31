# Низкоуровневые действия для wb_scrapper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import time


from robots.base.base import BaseRobot


class BaseSeleniumRobot(BaseRobot):
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.config = config or {}
        self.driver = self._init_driver()
        print(f"[DEBUG] driver config: {self.config}")

    def _init_driver(self):
        options = Options()
        if self.config.get("headless", True):
            options.add_argument("--headless")
        return webdriver.Chrome(options=options)

    def open_homepage(self):
        url = self.config["start_url"]
        self.driver.get(url)
        self._random_delay()
        self.wait_for_load()

    def wait_for_load(self):
        """Ожидание полной загрузки с проверкой состояния"""
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        # Дополнительная проверка на отсутствие загрузчиков
        try:
            self.wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, ".loading, .spinner, [data-loading]")))
        except:
            pass
        
        self._random_delay(0.5, 2.0)


    def _random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Случайная задержка для имитации человека"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)


    def human_scroll(self, pixels: int = None):
        """Имитация человеческого скролла"""
        if pixels is None:
            pixels = random.randint(200, 800)
        
        # Плавный скролл
        current_position = self.driver.execute_script("return window.pageYOffset")
        target_position = current_position + pixels
        
        steps = random.randint(5, 15)
        step_size = pixels / steps
        
        for i in range(steps):
            self.driver.execute_script(f"window.scrollTo(0, {current_position + step_size * (i + 1)})")
            time.sleep(random.uniform(0.05, 0.15))
        
        self._random_delay(0.2, 0.8)


    def human_click(self, element):
        """Клик с имитацией человека"""
        # Наведение курсора
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self._random_delay(0.2, 0.5)
        
        element.click()
        self._random_delay(0.3, 0.7)

    def close(self):
        if getattr(self, "driver", None):
            self.driver.quit()

    def __del__(self):
        self.close()
