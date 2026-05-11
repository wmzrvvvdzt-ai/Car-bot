import asyncio
from aiogram import Bot, Dispatcher

TOKEN = "8590083060:AAHzISyE09bEMp-m5HDJs-BoILHCL456cCA"

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    print("Bot started...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
