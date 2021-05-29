from __future__ import annotations

from datetime import datetime
from typing import Optional

from wechaty import Room
from wechaty import Contact
from wechaty import Message


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import wechaty

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tsadmin:123456@hackathon2021.localtunnel.chatie.io:5432/pgsqltest'

db = SQLAlchemy(app)


class DBRoom(db.Model):
    __tablename__ = 'room'
    room_id = db.Column(db.String(256), primary_key=True)
    topic = db.Column(db.String(256))
    member_num = db.Column(db.Integer)

    @staticmethod
    async def get(wechaty_room: Room) -> DBRoom:
        """get or create room based on wechaty room object"""

        room = DBRoom.query.filter(DBRoom.room_id == wechaty_room.room_id).first()
        if not room:
            room = DBRoom()
            room.room_id = wechaty_room.room_id

            await wechaty_room.ready()
            topic = await wechaty_room.topic()
            room.topic = wechaty_room.payload.topic
            room.member_num = len(wechaty_room.payload.member_ids)

            db.session.add(room)
            db.session.commit()

        return room


class DBContact(db.Model):
    __tablename__ = 'user'

    contact_id = db.Column(db.String(256), primary_key=True)
    name = db.Column(db.String(40))
    alias = db.Column(db.Text)

    weixin = db.Column(db.String(30))
    address = db.Column(db.String(30))
    city = db.Column(db.String(30))


    @staticmethod
    async def get(wechaty_contact: Contact) -> DBContact:
        """get or create contact based on Wechaty contact object"""
        contact = DBContact.query.filter(DBContact.contact_id == wechaty_contact.contact_id).first()

        if not contact:
            contact = DBContact()
            contact.contact_id = wechaty_contact.contact_id

            await wechaty_contact.ready()
            contact.name = wechaty_contact.payload.name
            contact.alias = wechaty_contact.payload.alias
            contact.weixin = wechaty_contact.payload.weixin

            db.session.add(contact)
            db.session.commit()

        return contact


class DBMessage(db.Model):
    __tablename__ = 'message'

    message_id = db.Column(db.String(256), primary_key=True)

    message_type = db.Column(db.Integer)
    content = db.Column(db.Text)

    talker_id = db.Column(db.String(256))
    room_id = db.Column(db.String(256), nullable=True)
    to_contact_id = db.Column(db.String(256), nullable=True)

    time = db.Column(db.DateTime, default=datetime.now)

    @staticmethod
    async def add(message: Message):
        """add message to the database"""
        wechaty_talker: Contact = message.talker()
        talker: DBContact = await DBContact.get(wechaty_talker)

        wechaty_room: Optional[Room] = message.room()
        wechaty_to: Optional[Contact] = message.to()

        msg = DBMessage()
        msg.message_id = message.message_id
        msg.message_type = message.type()
        msg.talker_id = talker.contact_id
        msg.content = message.text()

        if wechaty_room and wechaty_room.room_id:
            await DBRoom.get(wechaty_room)
            msg.room_id = wechaty_room.room_id

        if wechaty_to and wechaty_to.contact_id:
            await DBContact.get(wechaty_to)
            msg.to_contact_id = wechaty_to.contact_id

        db.session.add(msg)
        db.session.commit()


def init_db():
    # db.drop_all(app=app)
    db.create_all(app=app)


if __name__ == "__main__":
    init_db()
