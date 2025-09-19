import contextlib
import asyncio

from loguru import logger

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .handlers import routers
from .config import cnf
from .database.core import init_psql
from .utils.scheduler import update_users_limits


bot = Bot(
    token=cnf.bot.TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher(
    bot=bot,
    storage=MemoryStorage()
)

scheduler = AsyncIOScheduler()

async def startup(bot: Bot) -> None:
    """
        Активируется при выключении
    :param bot: Bot
    :return:
    """
    # Init dbs
    await init_psql()
    # Setting bot
    dp.include_routers(*routers)
    await bot.delete_webhook()
    await bot.set_my_commands(
        commands=cnf.bot.COMMANDS,
        scope=BotCommandScopeDefault()
    )
    for admin in cnf.bot.ADMINS:
        with contextlib.suppress(TelegramBadRequest):
            await bot.set_my_commands(
                cnf.bot.COMMANDS + cnf.bot.ADMIN_COMMANDS,
                scope=BotCommandScopeChat(chat_id=admin)
            )

    scheduler.add_job(
        update_users_limits,
        trigger='cron',
        hour=00, minute=00
    )

    logger.info('=== Bot started ===')


async def shutdown(bot: Bot) -> None:
    """
        Активируется при выключении
    :param bot: Bot
    :return:
    """
    await bot.close()
    await dp.stop_polling()

    logger.info('=== Bot stopped ===')


async def main() -> None:
    """
        Start the bot
    :return:
    """
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Exit')

