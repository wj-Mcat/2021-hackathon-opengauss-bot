
from re import S
from typing import ContextManager, List
from flask import jsonify
from datetime import datetime, timedelta
import jieba
import emoji
from collections import Counter, defaultdict
from advertools import extract_emoji

from flask.app import Flask
from src.db import app, db, DBRoom, DBContact, DBMessage

def success(data):
    return jsonify(dict(
        code=20000,
        data=data
    ))

@app.route("/room-members", methods=['GET'])
def get_room_members():
    members = DBContact.query.all()
    return success(len(members))

@app.route('/one-week-messages', methods=['GET'])
def get_one_week_messages():
    one_week_ago = datetime.now() - timedelta(days=7)
    messages = DBMessage.query.filter(DBMessage.time > one_week_ago).all()
    return success(len(messages))

@app.route('/freq-message', methods=['GET'])
def get_fre_message():
    one_week_ago = datetime.now() - timedelta(days=7)

    messages: List[DBMessage] = DBMessage.query.filter(DBMessage.time > one_week_ago).all()

    mini_time = min([message.time for message in messages])
    max_time = max([message.time for message in messages])

    start_time, end_time = mini_time, mini_time + timedelta(hours=1)

    blocks = []

    while True:
        if start_time > max_time:
            break

        time_block_messages = [message for message in messages if message.time >= start_time and message.time < end_time]
        blocks.append(len(time_block_messages))

        start_time, end_time = end_time, end_time + timedelta(hours=1)

    timelines = [f'{i+1}h' for i in range(len(blocks))]
    assert sum(blocks) == len(messages)

    return success(dict(times=timelines, count=blocks))


def is_question(text) -> bool:
    schemas = ['?', '什么时候', '为什么', '哪儿']
    for schema in schemas:
        if schema in text:
            return True
    return False

@app.route("/question-answer-count", methods=['GET'])
def get_question_answer_count():

    messages: List[DBMessage] = DBMessage.query.filter().all()
    messages = [message for message in messages if is_question(message.content)]
    return success(len(messages))

@app.route("/question-answer", methods=['GET'])
def get_question_answer():

    messages: List[DBMessage] = DBMessage.query.filter().all()
    messages = [message for message in messages if is_question(message.content)]
    res = []
    for message in messages:
        room = DBRoom.query.filter(DBRoom.room_id == message.room_id).first()
        time = datetime.strftime(message.time, '%Y-%m-%d %H:%M:%S')
        contact = DBContact.query.filter(DBContact.contact_id == message.talker_id).first()
        data = {
            "datetime": time,
            "content": message.content
        }
        if room:
            data['room'] = room.topic
        if contact:
            data['talker'] = contact.alias or contact.name
        res.append(data)

    return success(res)


@app.route("/word-cloud", methods=['GET'])
def get_word_count():

    messages: List[DBMessage] = DBMessage.query.filter().all()
    tokens = []
    for message in messages:
        sentence_tokens = jieba.lcut(message.content)
        tokens.extend(sentence_tokens)

    counter = Counter(tokens)
    
    stop_words = ['我', '@', '的', '(', ')', '各位', '社区', '大家', ',', '[', ']', '，', '（', '）', '合十']
    for stop_word in stop_words:
        if stop_word in counter:
            counter.pop(stop_word)
    
    res = [[word, count] for word, count in counter.items() if count > 2]
    
    return success(res)

@app.route("/top_emoji", methods=['GET'])
def get_top_emoji():

    messages: List[DBMessage] = DBMessage.query.filter().all()
    tokens = []

    for message in messages:
        emojis = extract_emoji(message.content)
        emojis = emojis['emoji']
        for emoji in emojis:
            tokens.extend(emoji)

    counter = Counter(tokens)

    emoji_list = list(counter.keys())
    emoji_count =  list(counter.values())
    
    return success(dict(list=emoji_list, count=emoji_count))

@app.route("/great_person", methods=['GET'])
def get_great_person():

    messages: List[DBMessage] = DBMessage.query.filter().all()
    
    member_count = defaultdict(int)

    for message in messages:
        member_count[message.talker_id] += 1

    name_count = defaultdict(list)
    for contact_id, count in member_count.items():
        contact: DBContact = DBContact.query.filter(DBContact.contact_id == contact_id).first()
        if contact:
            name_count[contact.name] = count

    name_list = list(name_count.keys())
    name_count =  list(name_count.values())
    
    return success(dict(names=name_list, count=name_count))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
