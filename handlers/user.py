from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboard.button_template import admin_kb, start_kb
from keyboard.keyboard_builder import make_row_inline_keyboards


user = Router()


@user.message(CommandStart())
async def start(message: Message):
	inline_kb = make_row_inline_keyboards(start_kb)
	await message.answer('hello', reply_markup=inline_kb)