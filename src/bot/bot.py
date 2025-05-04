from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import config
from parser.api import API
from parser.models import Vacancy
from db import DataBase

import logging
import asyncio

class VacancyBot:
    
    def __init__(self):

        self.bot = Bot(token=config.BOT_TOKEN)
        self.api = API()
        self.db = DataBase()
        self.dp = Dispatcher()
        self.register_handlers()

    def register_handlers(self):

        self.dp.message.register(self.send_welcome, Command("start"))
        self.dp.message.register(self.send_vacancies, Command("vacancies"))

    async def send_welcome(self, message: types.Message):

        await message.reply(
            "Привет! Я бот для поиска вакансий.\n"
            "Используйте команды:\n"
            "/vacancies - вакансии по умолчанию\n"
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

    
    async def run(self):
        await self.dp.start_polling(self.bot)
