import psutil


def check_ncalayer_running() -> bool:
    for proc in psutil.process_iter(['name']):
        try:
            if 'NCALayer' in proc.info['name']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False
