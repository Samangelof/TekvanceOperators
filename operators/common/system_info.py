import psutil
import platform
import uuid


def get_mac_address():
    """Возвращает MAC-адрес устройства"""
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                return addr.address
    return None

def get_machine_name():
    """Возвращает имя машины"""
    return platform.node()

def get_device_uuid():
    """Возвращает уникальный идентификатор устройства"""
    return str(uuid.UUID(int=uuid.getnode()))




# mac_address = get_mac_address()
# machine_name = get_machine_name()

# print(f'Unique ID: {"1747079261_fe21f7d8-4191-4712-84ee-27a9ccca8974"}')
# print(f"MAC: {mac_address}")
# print(f"Machine Name: {machine_name}")
# print(f"Machine verified: True")
# print(f"Machine status: True")
