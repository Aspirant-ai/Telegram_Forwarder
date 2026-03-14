import asyncio
import importlib

from forwarder import LOGGER, bot
from forwarder.modules import ALL_MODULES

for module in ALL_MODULES:
    importlib.import_module("forwarder.modules." + module)


def run():
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    LOGGER.info("Starting bot...")
    asyncio.set_event_loop(asyncio.new_event_loop())
    bot.run_polling()
