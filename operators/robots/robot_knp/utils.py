import psutil
import os
from common.logger import get_logger


logger = get_logger("utils_knp")


def check_ncalayer_running() -> bool:
    for proc in psutil.process_iter(['name']):
        try:
            if 'NCALayer' in proc.info['name']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def find_eds_file(folder_path: str) -> str:
    """
    Ищет файл в папке, имя которого начинается с 'AUTH_RSA256' или 'GOST512'.
    Возвращает полный путь к найденному файлу или None, если файл не найден.
    """
    try:
        logger.info(f"[SEARCH] Поиск файлов в папке: {folder_path}")

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                if file_name.startswith("AUTH_RSA256") or file_name.startswith("GOST512"):
                    logger.info(f"[FOUND] Найден файл: {file_path}")
                    return file_path
        logger.info(
            f"[NOT FOUND] Файлы с нужным названием не найдены в папке: {folder_path}")
        return None
    except FileNotFoundError:
        logger.error(f"[ERROR] Папка '{folder_path}' не найдена.")
    except PermissionError:
        logger.error(f"[ERROR] Нет доступа к папке '{folder_path}'.")
    except Exception as Err:
        logger.error(
            f"[ERROR] Ошибка при поиске EDS файла в {folder_path}: {Err}")
    return None


def extract_password_from_folder_name(folder_name: str) -> str:
    """
    Извлекает пароль из имени папки.
    Считается, что пароль всегда является последним элементом в имени папки, разделенным пробелами.

    :param folder_name: Имя папки.
    :return: Извлеченный пароль.
    """
    try:
        logger.info(
            f"[PROCESS] Извлечение пароля из имени папки: {folder_name}")

        parts = folder_name.strip().split()
        if not parts:
            raise ValueError(
                f"Папка '{folder_name}' имеет некорректный формат (пустое имя).")

        password = parts[-1]
        logger.info(f"[EXTRACTED] Извлечен пароль: {password}")
        return password
    except ValueError as vErr:
        logger.error(
            f"[ERROR] Некорректное имя папки: {folder_name}. Ошибка: {vErr}")
    except Exception as Err:
        logger.error(
            f"[ERROR] Ошибка при извлечении пароля из имени папки '{folder_name}': {Err}")
        raise
