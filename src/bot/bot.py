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

        self.dp.message.register(self.send_welcome, Command("start"))
        self.dp.message.register(self.send_vacancies, Command("vacancies"))
        self.dp.message.register(self.search_vacancies, Command("search"))

    async def send_welcome(self, message: types.Message):

        await message.reply(
            "Привет! Я бот для поиска вакансий.\n"
            "Используйте команды:\n"
            "/vacancies - вакансии по умолчанию\n"
            "/search <запрос> <регион> - кастомный поиск"
        )

    async def send_vacancies(self, message: types.Message):

        try:
            vacancies = await self.api.get_vacancies(config.DEFAULT_SEARCH_QUERY, config.DEFAULT_AREA_ID, config.MAX_VACANCIES)  

            if not vacancies:
                await message.reply("Вакансий не найдено.")
                return

            for vacancy in vacancies[:5]:
                await message.reply(vacancy.formatted())  

        except Exception as e:
            
            logging.error(f"Ошибка в send_vacancies: {e}")
            await message.reply(f"Произошла ошибка при обработке запроса: {e}")

    async def search_vacancies(self, message: types.Message): #пока не работает!
        
        try:
            _, query, area = message.text.split(maxsplit=2)
            area = int(area)

        except ValueError:
            await message.reply("Используйте: /search <запрос> <id региона>")
            return

        try:
            vacancies = self.api.get_vacancies(query, area)

            if not vacancies:
                await message.reply("По вашему запросу ничего не найдено")
                return

            for vacancy in vacancies:
                await message.reply(vacancy.formatted()) 

        except Exception as e:
            logging.error(f"Ошибка в search_vacancies: {e}")
            await message.reply(f"Произошла ошибка при обработке запроса: {e}")
    
    async def run(self):
        await self.dp.start_polling(self.bot)
