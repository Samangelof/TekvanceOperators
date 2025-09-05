import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from operators.common.selenium_actions import SeleniumActions
from common.logger import get_logger
from robots.base.base import BaseRobot
from robots.robot_knp.utils import find_eds_file, extract_password_from_folder_name


logger = get_logger("core_knp")


class KnpBehavior(BaseRobot):
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.config = config or {}
        self.driver = self._init_driver()
        self.actions = SeleniumActions(self.driver, logger, self.config)
        logger.debug(f"[DEBUG] driver config: {self.config}")

    def open_homepage(self):
        url = self.config["start_url"]
        self.driver.get(url)
        self.wait_for_load()

    def wait_for_load(self):
        """Ожидание полной загрузки с проверкой состояния"""
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda d: d.execute_script(
            "return document.readyState") == "complete")

        try:
            wait.until_not(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".loading, .spinner, [data-loading]")))
        except:
            pass

    def switch_language_to_russian(self):
        self.actions.wait_and_click(
            By.XPATH, "//div[contains(@class, 'lang-switcher')]//a[text()='Русский']", desc="ссылку 'Русский'")

    def login_by_cert(self):
        self.actions.wait_and_click(
            By.CSS_SELECTOR, ".enter-by-cert-button", desc="кнопку 'Войти по ЭЦП'")

    def select_cert_from_dir(self, folder_path: str):
        """Выбрать ЭЦП из указанной папки."""

        logger.info(f"[CERT] Работаем с папкой: {folder_path}")

        self.login_by_cert()
        
        folder_name = os.path.basename(folder_path)

        eds_file = find_eds_file(folder_path)
        if not eds_file:
            logger.warning(f"[CERT] Файл ЭЦП не найден в: {folder_path}")
            return False

        password = extract_password_from_folder_name(folder_name)
        if not password:
            logger.warning(f"[CERT] Пароль не найден, пропуск: {folder_path}")
            return False

        self.actions.wait_for_presence(By.CSS_SELECTOR, ".modal-dialog", desc="модальное окно")

        file_input = self.actions.wait_for_presence(
            By.CSS_SELECTOR, "input.custom-file-input", desc="input для файла ЭЦП"
        )
        
        if not file_input:
            logger.error("[CERT] Не найден input для загрузки ЭЦП")
            return False
        
        self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(eds_file)
        logger.debug(f"[CERT] Загружен файл: {eds_file}")

        pwd_input = self.actions.wait_for_input_ready(
            By.XPATH,
            "//input[@type='password' and contains(@class, 'form-control') and contains(@class, 'listBox')]",
            desc="поле пароля",
            timeout=10
        )
        if not pwd_input:
            logger.error("[CERT] Не найдено поле для ввода пароля")
            return False
            
        pwd_input.clear()
        pwd_input.send_keys(password)
        logger.debug(f"[CERT] Введeн пароль: {password[:2]}***")

        self.actions.wait_for_presence(
            By.XPATH, "//button[contains(text(), 'Ok') and not(@disabled)]",
            desc="активная кнопка 'Ok'"
        )

        self.actions.wait_and_click(
            By.XPATH, "//button[contains(text(), 'Ok') and not(@disabled)]",
            desc="кнопка 'Ok'"
        )

        alert = self.actions.wait_for_presence(
            By.CSS_SELECTOR, ".alert-danger", timeout=3, raise_on_timeout=False, desc="ошибка авторизации"
        )

        if alert:
            text = alert.text.strip()
            if "Срок действия Вашего сертификата" in text:
                logger.warning(f"[CERT] Сертификат истек: {folder_path}")
                return False
            if "Введите верный пароль" in text:
                logger.warning(f"[CERT] Неверный пароль: {folder_path}")
                return False

        self.actions.wait_and_click(
            By.XPATH, "//button[contains(text(), 'Выбрать')]", desc="кнопка 'Выбрать'"
        )

        #! Заделка на будущее для треккинга запросов и ответов для ловли ошибок со стороны веб ресурса
        # for entry in self.driver.get_log("performance"):
        #     msg = json.loads(entry["message"])
        #     method = msg.get("message", {}).get("method")
        #     if method == "Network.requestWillBeSent":
        #         url = msg["message"]["params"]["request"]["url"]
        #         logger.success(f"REQ: {url}")
        #     elif method == "Network.responseReceived":
        #         resp = msg["message"]["params"]["response"]
        #         logger.success(f"RESP: {resp['status']} {resp['url']}")


        logger.info(f"[CERT] Успешно выбран сертификат: {folder_path}")
        return True

    def logout(self):
        self.actions.wait_and_click(
            By.XPATH, "//a[@title='Выход']", desc="кнопка 'Выход'"
        )

    #* --
    def close(self):
        if getattr(self, "driver", None):
            self.driver.quit()

    def __del__(self):
        self.close()
