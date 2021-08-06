import string
from datetime import datetime

from socketsio import socketio
from app import app
from chat.models import ChatRoom, MessageRecipients, MessageMedia, Message, ChatUser
from utils.common import generate_response
from utils.http_code import *
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms, send
import json
from chat.selectors import get_rooms
from app import session
from flask import request
from utils.services.email_service import send_chat_notification


@socketio.on('connected')
def connect(data):
    print('================connnected=========')
    if not check_if_sid_exists(data):
        session.chat_clients[data['sid']] = {
            'sid': request.sid,
            'user': data['user']
        }


@socketio.on('disconnect')
def disconnect():
    print('client disconnected')
    try:
        del (session.chat_clients[request.sid])
    except:
        pass


def check_if_sid_exists(data):
    try:
        sid = session.chat_clients[data['sid']]
        return True
    except:
        return False


@socketio.on('get_chats')
def get_chats(data):
    print('get chats >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    user = data['user']
    chats = get_rooms(data, user['user_id'])
    emit('set_chats', {'chats': [chat.to_json() for chat in chats]})


@socketio.on('typing_start')
def typing_start(data):
    chat_room = ChatRoom.objects(id=data['room']).get()
    clients = get_chat_clients(chat_room)
    for cl in clients:
        emit('show_start_typing', data['user'], broadcast=False, room=cl)


@socketio.on('typing_end')
def typing_start(data):
    chat_room = ChatRoom.objects(id=data['room']).get()
    clients = get_chat_clients(chat_room)
    for cl in clients:
        emit('show_end_typing', data['user'], broadcast=False, room=cl)


@socketio.on("new_room_create")
def create_new_channel(data):
    print(data)
    print('New channel')
    """ Checks whether a channel can be created. If so, this updates the
        channel list and broadcasts the new channel.
    """
    # channel = clean_up_channel_name(data["channel"])
    user = data['user']
    error = validate_room(data, user)
    if error:
        emit("room_creation_failed", error, broadcast=False)
    chat_room = ChatRoom(name=data['name'] if 'name' in data else '')
    chat_room.creator = ChatUser(**user)
    chat_room.is_group = data['is_group'] if 'is_group' in data else True
    chat_room.save()
    admins = user
    chat_room.name = data['name']
    chat_room.admins = [ChatUser(**admins)]
    participants_input = data['participants'] if 'participants' else []
    participants = [ChatUser(**admins)]
    for participant in participants_input:
        participants.append(ChatUser(**participant))
    chat_room.participants = participants
    chat_room.save()
    clients = get_chat_clients(chat_room)
    for cl in clients:
        emit("add_room", {"channel": chat_room.to_json()}, broadcast=False, room=cl)


@socketio.on("new_message")
def new_message(data):
    print(data)
    print('New Message Loggedin')
    """ Processes the new message and stores it into the server list of
        messages given the room name. Broadcast the room and message.
    """
    errors = validate_message(data)
    if errors:
        emit("message_failed", errors, broadcast=False)
    timestamp = get_timestamp_trunc()
    user = data['user']
    sender = user
    room_data = ChatRoom.objects.get(id=data['room'])
    recipients = []
    for participant in room_data.participants:
        message_recipients = MessageRecipients(recipient=participant)
        message_recipients.room = room_data
        recipients.append(message_recipients)

    message = Message(sender=sender)
    message.type = data['type']
    message.message_body = data['message_body']
    message.recipients = recipients
    message.save()
    data = {
        "room": data['room'],
        "message_body": message.to_json(),
        "timestamp": timestamp,
        "sender": sender
    }
    # clients = get_chat_clients(room_data)
    # try:
    #     send_email_notification(room_data, message.message_body, user.email)
    # except Exception as e:
    #     print(e)

    clients = get_chat_clients(room_data)
    for cl in clients:
        emit("message_broadcast", data, broadcast=False, room=cl)


def send_email_notification(room_data, message_body, sender_email):
    recipient_emails = list
    for participant in room_data.participants:
        is_user_found = False
        for key, value in session.chat_clients.items():
            if str(participant.id) == value['user']['id']:
                is_user_found = True
        if not is_user_found:
            recipient_emails.append(participant.email)
    send_chat_notification(recipient_emails, message_body, sender_email)


def get_chat_clients(room_data):
    clients = []
    print('chat clients', session.chat_clients.items())

    for participant in room_data.participants:
        print(participant.user_id)
        for key, value in session.chat_clients.items():
            if str(participant.user_id) == value['user']['user_id']:
                clients.append(key)
    print(clients)
    return clients


def get_timestamp_trunc():
    """ Grabs the timestamp rounds the decimal point to deciseconds.
        For example:
        '2019-07-04 00:18:39.532357' becomes
        '2019-07-04 00:18:39.5'
    """
    timestamp = str(datetime.now())
    return timestamp[:-5]


def validate_room(data, user):
    if 'participants' not in data or not type(data['participants']) is list:
        return generate_response(message='invalid participants', status=HTTP_400_BAD_REQUEST)
    if 'is_group' in data:
        if data['is_group']:
            if 'name' not in data or not data['name']:
                return generate_response(message='Group name is required', status=HTTP_400_BAD_REQUEST)
            if ChatRoom.objects(name=data['name']):
                return generate_response(message='Group with this name is already exists', status=HTTP_400_BAD_REQUEST)
        # else:
        #     chat_room = ChatRoom.objects(
        #         participants__user_id__in=[user['user_id'], data['participants'][0]['user_id']])
        #     if chat_room:
        #         return generate_response(data=chat_room[0].to_json(), status=HTTP_200_OK)

    return None


def validate_message(data):
    if 'user' not in data or not data['user']:
        return generate_response(message='user is required', status=HTTP_400_BAD_REQUEST)
    if 'room' not in data or not data['room']:
        return generate_response(message='room is required', status=HTTP_400_BAD_REQUEST)
    if 'message_body' not in data or not data['message_body']:
        return generate_response(message='message_body is required', status=HTTP_400_BAD_REQUEST)
    if 'type' not in data or not data['type']:
        return generate_response(message='type is required', status=HTTP_400_BAD_REQUEST)
    return None


def clean_up_channel_name(text: str) -> str:
    """ Clean up extra spaces and remove punctuation from channel name.
    """
    # Remove punctuation
    text = text.strip().translate(str.maketrans('', '', string.punctuation))

    # Remove extra spaces by splitting spaces and rejoining
    text = ' '.join(text.split())

    return text


def valid_channel(channel: str) -> bool:
    """ Checks whether the channel is a valid channel name.
    """
    if channel == "":
        return False
    return True
