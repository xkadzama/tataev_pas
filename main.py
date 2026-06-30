import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from settings.config import ConfigBot


async def main():
	bot = Bot(token=ConfigBot.API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()

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


