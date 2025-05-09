from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from config import config
from parser.api import API
from parser.models import Vacancy
from .states import SearchStates

import logging


router = Router()

class VacancyBot:
    def __init__(self):
        self.bot = Bot(token=config.BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.api = API()
        self.user_searches = {}
        self.user_messages = {}

        self.dp.include_router(router)
        self.register_handlers()

    def register_handlers(self):
        @router.message(Command("start"))
        async def start(message: types.Message):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔍 Начать поиск", callback_data="search"),
                    InlineKeyboardButton(text="ℹ Помощь", callback_data="start")
                ],
                [
                    InlineKeyboardButton(text="🌍 Выбрать город", callback_data="select_city")
                ]
            ])
            await message.answer(
                "Привет! Я бот для поиска вакансий.\n"
                "Нажмите кнопку ниже или используйте команды:",
                reply_markup=keyboard
            )

        @router.message(Command("search"))
        async def begin_search(message: types.Message):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🌍 Выбрать город", callback_data="select_city")]
            ])
            await message.answer("Сначала выберите город:", reply_markup=keyboard)

        @router.callback_query(F.data == "select_city")
        async def select_city(callback: types.CallbackQuery, state: FSMContext):
            await state.set_state(SearchStates.waiting_for_city)
            cities = [
                ("Москва", 1), ("Санкт-Петербург", 2),
                ("Новосибирск", 4), ("Екатеринбург", 3), ("Самара", 78)
            ]
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=name, callback_data=f"city_{cid}")]
                    for name, cid in cities
                ]
            )
            await callback.message.answer("Выберите город:", reply_markup=keyboard)
            await callback.answer()

        @router.callback_query(F.data.startswith("city_"), SearchStates.waiting_for_city)
        async def set_city(callback: types.CallbackQuery, state: FSMContext):
            city_id = int(callback.data.split("_")[1])
            await state.update_data(city_id=city_id)
            await state.set_state(SearchStates.waiting_for_query)
            await callback.message.answer("Теперь введите поисковый запрос (например, Python):")
            await callback.answer()

        @router.message(SearchStates.waiting_for_query)
        async def handle_query(message: types.Message, state: FSMContext):
            user_data = await state.get_data()
            city_id = user_data.get("city_id")
            query = message.text.strip() or config.DEFAULT_SEARCH_QUERY

            vacancies = await self.api.get_vacancies(query, city_id, config.MAX_VACANCIES)
            if not vacancies:
                await message.reply("Вакансий не найдено.")
                await state.clear()
                return

            self.user_searches[message.from_user.id] = {
                'vacancies': vacancies,
                'current_page': 0
            }
            await self.show_vacancies_page(message.from_user.id, message.chat.id)
            await state.clear()

        @router.callback_query()
        async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
            user_id = callback.from_user.id
            data = callback.data

            if data.startswith(("prev_page_", "next_page_")):
                action, _, page = data.partition('_')
                page = int(page.split('_')[-1])

                if user_id in self.user_searches:
                    if action == "prev":
                        self.user_searches[user_id]['current_page'] = max(0, page - 1)
                    else:
                        self.user_searches[user_id]['current_page'] = page + 1

                    await callback.message.delete()
                    await self.show_vacancies_page(user_id, callback.message.chat.id)

            elif data == "search":
                await callback.message.answer("Введите команду /search или нажмите \"Выбрать город\".")

            elif data == "start":
                await callback.message.answer(
                    "Помощь:\n"
                    "/search — начать пошаговый поиск\n"
                    "Вы также можете использовать кнопки интерфейса."
                )

            await callback.answer()

    async def show_vacancies_page(self, user_id, chat_id):
        data = self.user_searches.get(user_id)
        if not data:
            await self.bot.send_message(chat_id, "Нет активного поиска.")
            return

        # Удаляем старые сообщения (если есть)
        message_ids = self.user_messages.get(user_id, [])
        for msg_id in message_ids:
            try:
                await self.bot.delete_message(chat_id, msg_id)
            except:
                pass

        self.user_messages[user_id] = []

        page = data['current_page']
        vacancies = data['vacancies']
        per_page = 3

        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_vacancies = vacancies[start_idx:end_idx]

        for vacancy in page_vacancies:
            msg = await self.bot.send_message(chat_id, vacancy.formatted())
            self.user_messages[user_id].append(msg.message_id)

        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton(
                text="⬅ Назад",
                callback_data=f"prev_page_{page}"
            ))

        if end_idx < len(vacancies):
            buttons.append(InlineKeyboardButton(
                text="Далее ➡",
                callback_data=f"next_page_{page}"
            ))

        city_button = InlineKeyboardButton(
            text="🌍 Выбрать город",
            callback_data="select_city"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            buttons,
            [city_button]
        ])

        nav_msg = await self.bot.send_message(
            chat_id,
            f"Страница {page + 1}",
            reply_markup=keyboard
        )
        self.user_messages[user_id].append(nav_msg.message_id)

    async def run(self):
        await self.dp.start_polling(self.bot)
