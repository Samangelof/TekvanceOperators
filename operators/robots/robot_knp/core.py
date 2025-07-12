# Низкоуровневые действия для robot_knp
from robots.base.base_selenium import BaseSeleniumRobot
import json
import os


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


class RobotKnpDriver(BaseSeleniumRobot):
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        options = {
            "headless": self.config.get("headless", True),
            "user_agent": self.config.get("user_agent"),
            "proxy": self.config.get("proxy"),
        }

        super().__init__(**options)

    def open_homepage(self):
        url = self.config["start_url"]
        self.driver.get(url)
        self.wait_for_load()

    # Пример: ожидание полного рендера
    def wait_for_load(self):
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
