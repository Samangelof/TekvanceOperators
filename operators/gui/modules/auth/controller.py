from common.api_service import api_service
from common.system_info import get_mac_address, get_machine_name


class AuthController:
    async def login(self, login: str, password: str) -> tuple[bool, str]:
        """Авторизация + верификация машины"""
        success, data = await api_service.get_jwt_token(login, password)
        if not success:
            return False, data.get("error", "Ошибка авторизации")

        unique_id = data.get("unique_id")
        mac = get_mac_address()
        hostname = get_machine_name()

        verified = await api_service.verify_machine(unique_id, mac, hostname, success)
        if not verified:
            return False, "Ошибка верификации машины"

        return True, "Успешно"