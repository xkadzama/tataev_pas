import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from settings.config import ConfigBot
from handlers.user import user as user_router
from handlers.admin import router as admin_router

from database.engine import async_engine
from database.models import Base


async def main():
	async with async_engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

	bot = Bot(token=ConfigBot.API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()
	dp.include_routers(admin_router)
	dp.include_routers(user_router)

	await dp.start_polling(bot)


if __name__ == '__main__':
	try:
		asyncio.run(main())
		logging.info('Bot run')
	except TelegramBadRequest as e:
		logging.error(f'Telegram bot API error: {e}')
	except KeyboardInterrupt:
		logging.info('Bot stopped by user')
	except Exception as e:
		logging.critical(f'Critical error: {e}')
