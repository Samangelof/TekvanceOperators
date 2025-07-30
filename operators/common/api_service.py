import aiohttp
from typing import Dict, Optional, Tuple, Any
from dotenv import load_dotenv
import os
import json
from common.logger import get_logger


logger = get_logger("api_service")

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "UNDIFINED_API_BASE_URL")
# TOKEN_AUTH_SAVE_PATH = os.getenv("TOKEN_AUTH_SAVE_PATH", "UNDEFINED_AUTH_SAVE_PATH")
TOKEN_AUTH_SAVE_PATH = os.path.expanduser(os.getenv("TOKEN_AUTH_SAVE_PATH", "~/.tekvance_token.json"))

class ApiService:
    """Сервис для работы с API"""
    def __init__(self, base_url: str = None):
        self.base_url = base_url or API_BASE_URL
        self.session = None
        self.access_token = None
        self.refresh_token_value = None
    
    async def ensure_session(self):
        """Создает сессию если она еще не создана"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    def save_tokens(self):
        with open(TOKEN_AUTH_SAVE_PATH, "w") as file:
            json.dump({
                "access": self.access_token,
                "refresh": self.refresh_token_value
            }, file)

    def load_tokens(self):
        if not os.path.exists(TOKEN_AUTH_SAVE_PATH):
            return False
        with open(TOKEN_AUTH_SAVE_PATH) as file:
            data = json.load(file)
            self.access_token = data.get("access")
            self.refresh_token_value = data.get("refresh")
        return True


    async def refresh_token(self):
        url = f"{self.base_url}/operators/api/token/refresh/"

        payload = {"refresh": self.refresh_token_value}
        await self.ensure_session()
        async with self.session.post(url, json=payload) as resp:
            try:
                data = await resp.json()
            except aiohttp.ContentTypeError:
                text = await resp.text()
                logger.error(f"Ошибка: ответ не JSON. Статус={resp.status}, тело={text}, payload={payload}")
                return False
            if resp.status == 200 and "access" in data:
                self.access_token = data["access"]
                self.save_tokens()
                return True
            return False
    
    async def api_request(self, method, endpoint, **kwargs):
        await self.ensure_session()
        headers = kwargs.pop("headers", {})
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        logger.debug(f"[api_request] {method} {endpoint} | Headers: {headers}")
        url = f"{self.base_url}{endpoint}"
        async with self.session.request(method, url, headers=headers, **kwargs) as resp:
            logger.debug(f"[api_request] Response: {resp.status} {await resp.text()}")
            if resp.status == 401 and self.refresh_token_value:
                logger.debug("[api_request] 401 detected, trying refresh_token_value")
                ok = await self.refresh_token()
                if not ok:
                    logger.debug("[api_request] Refresh token also invalid")
                    raise RuntimeError("Session expired, please login again.")
                headers["Authorization"] = f"Bearer {self.access_token}"
                logger.debug(f"[api_request] Retrying with refreshed token: {headers}")
                async with self.session.request(method, url, headers=headers, **kwargs) as resp2:
                    logger.debug(f"[api_request] Retry response: {resp2.status} {await resp2.text()}")
                    return await resp2.json()
            return await resp.json()


    async def verify_machine_auth(self, login, password):
        await self.ensure_session()
        url = f"{self.base_url}/operators/authenticate_machine/"
        payload = {"login": login, "password": password}
        async with self.session.post(url, json=payload) as response:
            data = await response.json()
            if response.status == 200:
                logger.info(f"Машина успешно авторизована: {login}")
                return True, data
            logger.warning(f"Ошибка авторизации машины: {response.status}, {data}")
            return False, data


    async def get_jwt_token(self, login, password):
        await self.ensure_session()
        url = f"{self.base_url}/operators/api/token/"

        
        payload = {"login": login, "password": password}
        
        async with self.session.post(url, json=payload) as response:
            data = await response.json()
            if response.status == 200 and "access" in data and "refresh" in data:
                self.access_token = data["access"]
                self.refresh_token_value = data["refresh"]
                self.save_tokens()
                logger.info(f"JWT получен для {login}")
                return True, data
            logger.warning(f"Ошибка получения токена: {response.status}, {data}")
            return False, data

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

    async def close(self):
        """Закрывает сессию"""
        if self.session:
            await self.session.close()
            self.session = None
    

api_service = ApiService()
api_service.load_tokens()
logger.debug(f"api_service.load_tokens()={api_service.load_tokens()}")

# login = "user2"
# password = "nqOSwzSVo_%]"

# async def perform_login(login: str, password: str):
#     logger.debug(f'[perform_login] Запуск проверки для {login}')


#     success, data = await api_service.login(login, password)
#     return success, data

# asyncio.ensure_future(perform_login(login, password))

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     # loop.run_until_complete(perform_login(login, password))
#     loop.run_until_complete(api_service.close())