import aiohttp
import logging
from typing import Dict, Optional, Tuple, Any


logger = logging.getLogger(__name__)

class ApiService:
    """Сервис для работы с API"""
    # base_url нужно будет вынести в конфиг
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
    
    async def ensure_session(self):
        """Создает сессию если она еще не создана"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Закрывает сессию"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def login(self, login: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Авторизация пользователя
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            
        Returns:
            Tuple[bool, Optional[Dict]]: (Успех операции, Данные ответа или None)
        """
        try:
            await self.ensure_session()
            
            url = f"{self.base_url}/operators/authenticate_machine/"
            payload = {
                "login": login,
                "password": password
            }
            
            async with self.session.post(url, json=payload) as response:
                data = await response.json()
                unique_id = data.get("unique_id")
                data["unique_id"] = unique_id
                if response.status == 200:
                    logger.info(f"Успешная аутентификация: {login}")
                    return True, data
                else:
                    logger.warning(f"Ошибка аутентификация: {response.status}, {data}")
                    return False, data
                    
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса авторизации: {e}", exc_info=True)
            return False, {"error": str(e)}
    
    async def verify_machine(
            self, 
            unique_id: str,
            mac_address: str, 
            machine_name: str, 
            success: bool
        ) -> bool:

        try:
            await self.ensure_session()
            
            url = f"{self.base_url}/operators/machines/verify/"
            payload = {
                "unique_id": unique_id, 
                "mac_address": mac_address,
                "machine_name": machine_name,
                "success": success,
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Успешная верификация машины: {mac_address}")
                    return True
                else:
                    data = await response.json()
                    logger.warning(f"Ошибка верификации машины: {response.status}, {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса верификации: {e}", exc_info=True)
            return False


api_service = ApiService()



# login = "user2"
# password = "nqOSwzSVo_%]"

# async def perform_login(login: str, password: str):
#     print(f'[perform_login] Запуск проверки для {login}')


#     success, data = await api_service.login(login, password)
#     return success, data

# asyncio.ensure_future(perform_login(login, password))

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     # loop.run_until_complete(perform_login(login, password))
#     loop.run_until_complete(api_service.close())