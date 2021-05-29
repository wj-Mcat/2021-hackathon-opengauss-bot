from __future__ import annotations
import sys, os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

import asyncio

from wechaty import (
    Wechaty
)
from wechaty_plugin_contrib import DingDongPlugin
from wechaty_puppet import get_logger
from src.db import DBRoom, DBContact

from src.skills import RoomMessagePlugin, RoomMessagePluginOptions

logger = get_logger("Bot")


class Bot(Wechaty):
    async def on_ready(self, payload):
        # init the room and room members
        logger.info("init the room mmebers and room message")
        
        rooms = await self.Room.find_all()
        for room in rooms:
            await room.ready()
            if '黑客松' in room.payload.topic:
                await DBRoom.get(room)

                # fetch all of room members
                room_members = await room.member_list()
                for room_member in room_members:
                    await DBContact.get(room_member)
    


async def main():
    bot = Bot()

    room_message_plugin_options = RoomMessagePluginOptions()
    room_message_plugin = RoomMessagePlugin(room_message_plugin_options)

    ding_dong_plugin = DingDongPlugin()
    
    bot.use(room_message_plugin)
    bot.use(ding_dong_plugin)

    await bot.start()   


asyncio.run(main())
