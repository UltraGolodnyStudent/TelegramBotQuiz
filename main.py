import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import API_TOKEN
from dataBase import create_table

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
