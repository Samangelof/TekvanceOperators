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

    def open_account_page(self) -> bool:
        """Открыть страницу лицевого счета (с авто-ретраем + JS-клик при фейле)"""
        main_xpath = "//div[contains(@class, 'iceMnuBarItem')]//span[normalize-space()='Лицевой счет']"
        sub_xpath = "//div[contains(@class, 'subMenu')]//a[@href='/knp/p_accounts/card/']"

        for attempt in (1, 2):
            try:
                main_item = self.actions.wait_for_presence(
                    By.XPATH, main_xpath,
                    desc="пункт меню 'Лицевой счет'",
                    timeout=10
                )
                if not main_item:
                    raise RuntimeError("верхний пункт меню не найден")
                main_item.click()

                account_link = self.actions.wait_for_presence(
                    By.XPATH, sub_xpath,
                    desc="ссылка 'Лицевой счет'",
                    timeout=10
                )
                if not account_link:
                    raise RuntimeError("ссылка не найдена")

                try:
                    account_link.click()
                except Exception:
                    logger.warning("[NAV] Обычный клик не сработал, пробуем JS-клик")
                    self.driver.execute_script("arguments[0].click();", account_link)

                self.wait_for_load()
                logger.info(f"[NAV] Перешли на страницу лицевого счета (попытка {attempt})")
                return True

            except Exception as e:
                logger.warning(f"[NAV] Ошибка при переходе на лицевой счет (попытка {attempt}): {e}")
                self.driver.refresh()
                self.wait_for_load()

        logger.error("[NAV] Не удалось открыть страницу лицевого счета")
        return False

    def request_account_balance(self) -> bool:
        """Запросить сальдо лицевого счета"""
        try:
            self.actions.wait_and_click(
                By.XPATH,
                "//button[contains(text(), 'Запросить сальдо ЛС')]",
                desc="кнопка 'Запросить сальдо ЛС'",
                wait_for_visibility=True
            )
            self.wait_for_load()
            logger.info("[BALANCE] Отправлен запрос на получение сальдо ЛС")
            return True
        except Exception as e:
            logger.error(f"[BALANCE] Ошибка при запросе сальдо ЛС: {e}")
            return False

    def check_table_and_screenshot_negatives(self, save_dir: str = "screens") -> list[str]:
        """
        Проверить таблицу сальдо и сохранить скриншоты строк с отрицательными значениями.
        Возвращает список путей к сохранённым скринам.
        """
        os.makedirs(save_dir, exist_ok=True)
        saved: list[str] = []

        try:
            table = self.actions.wait_for_presence(
                By.ID, "dataTable", desc="таблица сальдо", timeout=5, raise_on_timeout=False
            )
            if not table:
                logger.info("[TABLE] Таблица сальдо отсутствует, пропуск")
                return saved

            self.driver.execute_script("arguments[0].scrollIntoView(true);", table)

            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            if not rows:
                logger.info("[TABLE] В таблице нет строк, пропуск")
                return saved

            for idx, row in enumerate(rows, start=1):
                negatives = row.find_elements(By.CSS_SELECTOR, "span.text-red")
                if negatives:
                    path = os.path.join(save_dir, f"row_{idx}.png")
                    row.screenshot(path)
                    saved.append(path)
                    logger.warning(
                        f"[TABLE] Отрицательное значение в строке {idx}, скриншот: {path}"
                    )

        except Exception as e:
            logger.error(f"[TABLE] Ошибка при проверке таблицы: {e}")

        return saved

    def open_notifications_page(self) -> bool:
        """
        Открыть страницу 'Уведомления / Извещения / Решения',
        нажать 'Найти' и дождаться окончания загрузки (с авто-ретраем + JS-клик при фейле)
        """
        main_xpath = "//div[contains(@class, 'iceMnuBarItem')]//span[normalize-space()='Уведомления/ Извещения/ Решения']"
        sub_xpath = "//div[contains(@class, 'subMenu')]//a[@href='/knp/notifications/registry/']"
        find_btn_xpath = "//button[normalize-space()='Найти']"
        loader_css = ".thin-loader"

        for attempt in (1, 2):
            try:
                main_item = self.actions.wait_for_presence(
                    By.XPATH, main_xpath,
                    desc="пункт меню 'Уведомления/ Извещения/ Решения'",
                    timeout=10
                )
                if not main_item:
                    raise RuntimeError("верхний пункт меню не найден")
                main_item.click()

                notif_link = self.actions.wait_for_presence(
                    By.XPATH, sub_xpath,
                    desc="ссылка 'Уведомления / Извещения / Решения'",
                    timeout=10
                )
                if not notif_link:
                    raise RuntimeError("ссылка не найдена")

                try:
                    notif_link.click()
                except Exception:
                    logger.warning("[NAV] Обычный клик не сработал, пробуем JS-клик")
                    self.driver.execute_script("arguments[0].click();", notif_link)

                self.wait_for_load()

                self.actions.wait_and_click(
                    By.XPATH, find_btn_xpath,
                    desc="кнопка 'Найти'",
                    wait_for_visibility=True
                )

                #! Костыль. УБРАТЬ!
                from selenium.webdriver.support.ui import WebDriverWait
                WebDriverWait(self.driver, 20).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, loader_css))
                )

                self.wait_for_load()
                logger.info(f"[NAV] Перешли на уведомления, нажали 'Найти' и дождались загрузки (попытка {attempt})")
                return True

            except Exception as e:
                logger.warning(f"[NAV] Ошибка при переходе/поиске на уведомлениях (попытка {attempt}): {e}")
                self.driver.refresh()
                self.wait_for_load()

        logger.error("[NAV] Не удалось открыть уведомления и нажать 'Найти'")
        return False


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
