import asyncio
import logging

from bot.bot import VacancyBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def main():
    bot = VacancyBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())