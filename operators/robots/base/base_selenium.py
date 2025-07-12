from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from robots.base.base import BaseRobot


class BaseSeleniumRobot(BaseRobot):
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.config = config or {}
        self.driver = self._init_driver()

    def _init_driver(self):
        options = Options()
        if self.config.get("headless", True):
            options.add_argument("--headless")
        for arg in self.config.get("chrome_args", []):
            options.add_argument(arg)
        return webdriver.Chrome(options=options)

    def close(self):
        if getattr(self, "driver", None):
            self.driver.quit()

    def __del__(self):
        self.close()
