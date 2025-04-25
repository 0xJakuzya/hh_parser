from config import config
from parser.models import Vacancy

import requests
from typing import List
import aiohttp
import asyncio

class API:
    def __init__(self):

        self.base_url = config.HH_API_URL 

    async def get_vacancies(self, query: str, area: int, count: int) -> List[Vacancy]:

        params = {
            "text": query,
            "area": area,
            "per_page": count,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return [Vacancy(item) for item in data.get("items", [])] 
                        except aiohttp.ClientResponseError as e:
                            print(f"Ошибка при разборе JSON: {e}")
                            return [] 
                    else:
                        print(f"Ошибка HTTP: {response.status}")
                        return [] 

        except aiohttp.ClientError as e:
            print(f"Ошибка соединения с API: {e}")
            return [] 