import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN

dp = Dispatcher()

@dp.message()
async def echo(message):
    await message.answer(message.text)

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
