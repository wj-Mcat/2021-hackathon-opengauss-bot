from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from wechaty import (
    WechatyPlugin, Message, Wechaty,
    MessageType, WechatyPluginOptions
)

from src.db import DBRoom, DBMessage


@dataclass
class RoomMessagePluginOptions(WechatyPluginOptions):
    room_ids: List[str] = field(default_factory=list)


class RoomMessagePlugin(WechatyPlugin):

    def __init__(self, options: RoomMessagePluginOptions):
        super(RoomMessagePlugin, self).__init__(options)
        self.options: RoomMessagePluginOptions = options

    async def init_plugin(self, wechaty: Wechaty):
        """init the plugin"""
        rooms = await wechaty.Room.find_all()
        for room in rooms:
            await room.ready()
            if '黑客松' in room.payload.topic:
                self.options.room_ids.append(room.room_id)

    async def on_message(self, msg: Message):
        if msg.is_self():
            return

        room = msg.room()
        if not room:
            return

        print(room.room_id)
        # if room.room_id not in self.options.room_ids:
        #     return

        if MessageType.MESSAGE_TYPE_TEXT == msg.type():
            await DBMessage.add(msg)

