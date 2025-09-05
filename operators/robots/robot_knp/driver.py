import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from robots.robot_knp.core import KnpBehavior


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

class KnpDriver(KnpBehavior):
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

    
    def _init_driver(self):
        options = self.config["chrome_options"]
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Page.enable", {})
        return driver

