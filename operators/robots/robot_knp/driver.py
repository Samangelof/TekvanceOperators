import os
import json
import time
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from robots.robot_knp.core import BaseSeleniumRobot


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
print(f"[DEBUG] loading config from: {CONFIG_PATH}")

class RobotKnpDriver(BaseSeleniumRobot):
    def __init__(self, config=None, *args, **kwargs):
        if config is None:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)

        config['chrome_options'] = self._build_chrome_options(config)
        super().__init__(config=config)


    def _build_chrome_options(self, config) -> Options:
        options = Options()
        
        # Основные настройки
        if config.get("headless", True):
            options.add_argument("--headless=new")
        
        # Размер окна
        window_size = config.get("window_size", [1920, 1080])
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        
        # User-Agent
        if config.get("user_agent"):
            options.add_argument(f"--user-agent={config['user_agent']}")
        
        # Прокси
        if config.get("proxy"):
            options.add_argument(f"--proxy-server={config['proxy']}")
        
        # Антидетект аргументы
        stealth_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions-except",
            "--disable-plugins-discovery",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-features=VizDisplayCompositor,TranslateUI",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-sync",
            "--disable-default-apps",
            "--no-first-run",
            "--no-pings",
            "--no-zygote",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-background-networking",
            "--disable-background-mode",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-domain-reliability",
            "--disable-component-update",
            "--disable-permissions-api",
            "--disable-notifications",
            "--disable-desktop-notifications"
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
        
        # Исключения
        exclude_switches = config.get("exclude_switches", [])
        if exclude_switches:
            options.add_experimental_option("excludeSwitches", exclude_switches)
        
        # Отключить автоматизацию
        options.add_experimental_option("useAutomationExtension", False)
        
        # Prefs
        prefs = config.get("prefs", {})
        if prefs:
            options.add_experimental_option("prefs", prefs)
        
        return options

    def _setup_stealth(self):
        """Скрыть следы автоматизации"""
        # Удалить свойство webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Изменить user agent через CDP
        user_agent = self.config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": user_agent
        })
        
        # Установить viewport
        viewport = self.config.get("viewport_size", [1920, 1080])
        self.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": viewport[0],
            "height": viewport[1],
            "deviceScaleFactor": 1,
            "mobile": False
        })
        
        # Переопределить permissions
        self.driver.execute_cdp_cmd("Browser.grantPermissions", {
            "permissions": ["notifications", "geolocation"]
        })

    def open_homepage(self):
        url = self.config["start_url"]
        self.driver.get(url)
        self._random_delay()
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
        
        # Клик
        element.click()
        self._random_delay(0.3, 0.7)