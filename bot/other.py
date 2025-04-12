import logging
import aiohttp
import base64
import uuid
from typing import Dict, Any
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from os import getenv, path


bot = Bot(token=getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def get_logger(logger_name: str) -> logging.Logger:
    """
    Создание и настрайка логгера
    :param logger_name: Имя логгера
    :param log_type: Тип ('console' или 'file')
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    log_type = getenv('LOG_TYPE')
    if log_type == 'console':
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        handler = logging.FileHandler(filename=path.join(path.dirname(path.abspath(__file__)), 'logs.txt'), encoding='UTF-8')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class YooKassaApi:
    def __init__(self, shop_id: str, secret_key: str):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.auth = base64.b64encode(f"{shop_id}:{secret_key}".encode()).decode()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Basic {self.auth}",
            "Idempotence-Key": str(uuid.uuid4()),
            "Content-Type": "application/json",
            **kwargs.pop('headers', {})
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"https://api.yookassa.ru/v3/{endpoint}",
                headers=headers,
                **kwargs
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def create_payment(self, amount: float, return_url: str, metadata: dict) -> Dict[str, Any]:
        """Создает платеж и возвращает данные для оплаты"""
        payload = {
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "payment_method_data": {"type": "bank_card"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "metadata": metadata,
            "capture": True}
        return await self._request("POST", "payments", json=payload)
    
    async def get_payment(self, payment_id) -> Dict[str, Any]:
        return await self._request("GET", f"payments/{payment_id}")
    

yk = YooKassaApi(getenv("SHOP_ID"), getenv("SCID"))
    