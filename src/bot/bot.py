from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import config
from parser.api import API
from parser.models import Vacancy

import logging
import asyncio

class VacancyBot:
    
    def __init__(self):

        self.bot = Bot(token=config.BOT_TOKEN)
        self.api = API()
        self.dp = Dispatcher()
        self.register_handlers()

    def register_handlers(self):

        self.dp.message.register(self.start, Command("start"))
        self.dp.message.register(self.search, Command("search"))

    async def start(self, message: types.Message):

        await message.reply(
            "Привет! Я бот для поиска вакансий.\n"
            "Используйте команды:\n"
            "/search [запрос] [город] - для поиска вакансии\n"
        )

    async def search(self, message: types.Message):

        args = message.text.split()[1:]
        
        CITY_ID = {
            'Москва': 1,
            'санкт-петербург': 2,
            'новосибирск': 4,
            'екатеринбург': 3,
            'Самара': 78
        }

        city = None
        query_parts = []

        for arg in args:
            lower_arg = arg.lower()
            if lower_arg in CITY_ID and not city:
                city = lower_arg
            else:
                query_parts.append(arg)

        query = ' '.join(query_parts) if query_parts else config.DEFAULT_SEARCH_QUERY
        area_id = CITY_ID.get(city, config.DEFAULT_AREA_ID)

        try:
            vacancies = await self.api.get_vacancies(query, area_id, config.MAX_VACANCIES)  

            if not vacancies:
                await message.reply("Вакансий не найдено.")
                return

            for vacancy in vacancies[:5]:
                await message.reply(vacancy.formatted())  

        except Exception as e:
            
            logging.error(f"Ошибка в send_vacancies: {e}")

            await message.reply(f"Произошла ошибка при обработке запроса: {e}")

    
    async def run(self):
        await self.dp.start_polling(self.bot)
