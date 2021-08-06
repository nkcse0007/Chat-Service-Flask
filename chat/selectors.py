import json

from utils.common import generate_response
from utils.http_code import *
import datetime
import random
import os

from .models import MessageMedia, MessageRecipients, Message, ChatRoom


def get_rooms(input_data, user_id):
    rooms = ChatRoom.objects(participants__user_id__contains=user_id).select_related(3)

    for room in rooms:
        if not room['is_group']:
            if room['participants']:
                if user_id == room['participants'][0]['user_id']:
                    room['name'] = room['participants'][-1]['email']
                else:
                    room['name'] = room['participants'][0]['email']
    return rooms


def get_messages(input_data):
    room = ChatRoom.objects(id=input_data['room']).get()
    messages = Message.objects(recipients__room=input_data['room'])
    return generate_response(data={'room': room.to_json(), 'messages': [message.to_json() for message in messages]},
                             status=HTTP_200_OK)
