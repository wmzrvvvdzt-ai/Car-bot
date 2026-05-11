from aiogram import Router, types

router = Router()

@router.message()
async def start(message: types.Message):
    await message.answer("Бот работает ✅")
