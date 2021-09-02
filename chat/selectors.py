import json

from utils.common import generate_response
from utils.http_code import *
import datetime
import random
import os

from .models import MessageMedia, MessageRecipients, Message, ChatRoom


def get_rooms(input_data, user_id):
    rooms = ChatRoom.objects(participants__user_id__contains=user_id).order_by('-updated_at').select_related(3)

    for room in rooms:
        if not room['is_group']:
            if room['participants']:
                if user_id == room['participants'][0]['user_id']:
                    room['name'] = room['participants'][-1]['email']
                    room['image'] = room['participants'][-1]['profile_image']
                else:
                    room['name'] = room['participants'][0]['email']
                    room['image'] = room['participants'][0]['profile_image']
    return rooms


def get_messages(input_data):
    # import pdb;pdb.set_trace()
    room = ChatRoom.objects(id=input_data['room']).get().to_json()
    if not room['is_group']:
        if room['participants']:
            if input_data['user_id'] == room['participants'][0]['user_id']:
                room['name'] = room['participants'][-1]['email']
                room['image'] = room['participants'][-1]['profile_image']
            else:
                room['name'] = room['participants'][0]['email']
                room['image'] = room['participants'][0]['profile_image']
    # import pdb;
    # pdb.set_trace()
    messages = Message.objects(recipients__room=input_data['room'])
    unread_count = Message.objects(recipients__room=room['id'], recipients__is_read=False,
                                   recipients__recipient__user_id=input_data['user_id']).count()

    return generate_response(
        data={'room': room, 'messages': [message.to_json() for message in messages], 'unread_count': unread_count},
        status=HTTP_200_OK)
