from __future__ import annotations
import sys, os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

import asyncio, dotenv, os

from wechaty import (
    Wechaty
)


from src.skills import RoomMessagePlugin, RoomMessagePluginOptions


class Bot(Wechaty):
    pass


async def main():
    dotenv.load_dotenv()
    import os
    os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = ''
    bot = Bot()

    room_message_plugin_options = RoomMessagePluginOptions()
    room_message_plugin = RoomMessagePlugin(room_message_plugin_options)
    bot.use(room_message_plugin)

    await bot.start()


asyncio.run(main())
