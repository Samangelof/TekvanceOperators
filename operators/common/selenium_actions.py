from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException
)
from common.logger import get_logger


logger = get_logger("selenium_actions")

class SeleniumActions:
    def __init__(self, driver, logger, config: dict):
        self.driver = driver
        self.config = config
        self.timeout = 60

    def wait_and_click(self, by: By, value: str, desc: str = None, wait_for_visibility: bool = False, retries: int = 2):
        """
        Клик по элементу с ожиданием, с защитой от stale element.
        """
        attempt = 0
        while attempt <= retries:
            try:
                logger.info(f"Ожидание элемента: {desc or value}")
                wait = WebDriverWait(self.driver, self.timeout)

                if wait_for_visibility:
                    element = wait.until(EC.visibility_of_element_located((by, value)))
                else:
                    element = wait.until(EC.element_to_be_clickable((by, value)))

                logger.info(f"Клик по элементу: {desc or value}")
                element.click()
                return  # успех — выходим

            except StaleElementReferenceException:
                attempt += 1
                logger.warning(f"[STALE] Элемент {desc or value} устарел, повтор {attempt}/{retries}")
                if attempt > retries:
                    logger.error(f"[STALE] Не удалось кликнуть по {desc or value} после {retries} попыток.")
                    return
                continue

            except NoSuchElementException:
                logger.error(f"Элемент '{desc or value}' не найден.")
                return
            except ElementClickInterceptedException:
                logger.error(f"Клик по элементу '{desc or value}' перехвачен.")
                return
            except TimeoutException:
                logger.error(f"Тайм-аут при ожидании элемента '{desc or value}'.")
                return
            except WebDriverException as e:
                logger.error(f"WebDriver ошибка при клике '{desc or value}': {str(e)}")
                return
            except Exception as e:
                logger.error(f"Неизвестная ошибка при клике '{desc or value}': {str(e)}", exc_info=True)
                return

    def wait_for_presence(self, by: By, selector: str, desc: str = "элемент", timeout: int = 60, raise_on_timeout: bool = True):
        try:
            logger.info(f"[WAIT] Ожидание присутствия {desc}")
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, selector)))
            logger.info(f"[FOUND] Присутствует: {desc}")
            return element
        except TimeoutException:
            logger.warning(f"[TIMEOUT] Элемент '{desc}' не появился за {timeout} сек.")
            if raise_on_timeout:
                raise
            return None
        except WebDriverException as e:
            logger.error(f"[ERROR] WebDriver ошибка при ожидании {desc}: {str(e)}", exc_info=True)
            raise

    def wait_for_input_ready(self, by: By, selector: str, desc: str = "поле", timeout: int = 30):
        try:
            logger.info(f"[WAIT] Ожидание интерактивности {desc}")
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(lambda d: (
                (el := d.find_element(by, selector)).is_displayed() and el.is_enabled() and not el.get_attribute("disabled") and el
            ))
            logger.info(f"[READY] Интерактивен: {desc}")
            return element
        except TimeoutException:
            logger.warning(f"[TIMEOUT] Поле '{desc}' не стало активным за {timeout} сек.")
            raise
