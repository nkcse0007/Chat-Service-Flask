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
from mongoengine.queryset.visitor import Q
from utils.services.email_service import send_chat_notification


@socketio.on('connected')
def connect(data):
#    import pdb;pdb.set_trace()
    print('INSIDE CONNECTION -------------------------------------------------------------------------------------', 'CONNECTION ID', data['user']['user_id'])
    if not check_if_sid_exists(data):
        session.chat_clients[request.sid] = {
            'sid': request.sid,
            'user': data['user']
        }
    print('client_data', data)
    print(request.sid, 'SIDDDDDDDDDDDDDDDD')
    print('==========================================================================================================',
          session.chat_clients)


@socketio.on('disconnect')
def disconnect():
    try:
        user_offline = session.chat_clients[request.sid]
        print('INSIDE DISCONNECT -------------------------------------------------------------------------------------', 'CONNECTION ID', user_offline)
        del (session.chat_clients[request.sid])
        ChatRoom.objects(participants__user_id=user_offline['user_id']).update(
            set__participants__S__last_seen=datetime.now())
        emit("user_offline_show", user_offline, broadcast=True)
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
    print('INSIDE GET CHATS -------------------------------------------------------------------------------------')
    user = data['user']
    # import pdb;pdb.set_trace()
    chats = get_rooms(data, user['user_id'])
    final_chats = list()
    for chat in chats:
        chat = chat.to_json()
        chat['unread_messages_count'] = Message.objects(recipients__room=chat['id'], recipients__is_read=False,
                                                        sender__user_id=chat['participants'][0]['user_id'] if
                                                        chat['participants'][0]['user_id'] != user['user_id'] else
                                                        chat['participants'][1]['user_id']).count()
        final_chats.append(chat)
    emit('set_chats', {'chats': final_chats})


@socketio.on('typing_start')
def typing_start(data):
    print('INSIDE TYPING START -------------------------------------------------------------------------------------')
    chat_room = ChatRoom.objects(id=data['room']).get()
    clients = get_chat_clients(chat_room)
    for cl in clients:
        emit('show_start_typing', data, broadcast=False, room=cl['sid'])


@socketio.on('typing_end')
def typing_start(data):
    print('INSIDE TYPING END -------------------------------------------------------------------------------------')
    chat_room = ChatRoom.objects(id=data['room']).get()
    clients = get_chat_clients(chat_room)
    for cl in clients:
        emit('show_end_typing', data, broadcast=False, room=cl['sid'])


@socketio.on("new_room_create")
def create_new_channel(data):
#    import pdb;pdb.set_trace()
    print('INSIDE NEW CHANNEL -------------------------------------------------------------------------------------')
    # print(data)
    """ Checks whether a channel can be created. If so, this updates the
        channel list and broadcasts the new channel.
    """
    # channel = clean_up_channel_name(data["channel"])
    user = data['user']
    error = validate_room(data, user)
    if error:
        emit("room_creation_failed", error, broadcast=False)

    new_room = True
    chat_room = None
    if not data['is_group']:
        previous_room = ChatRoom.objects(Q(participants__user_id=data['participants'][0]['user_id']) & Q(
            participants__user_id=data['user']['user_id'])).first()
        if previous_room:
            new_room = False
            chat_room = previous_room
    if new_room:
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
    print(request.sid)
    print(clients, 'llllllllllllllllllllllllllllllllllllllllllllllll', clients)
    for cl in clients:
        emit("add_room", {"channel": chat_room.to_json()}, broadcast=True, room=cl['sid'])


@socketio.on("new_message")
def new_message(data):
    print('INSIDE NEW MESSAGE -------------------------------------------------------------------------------------')
    # print(data)
    """ Processes the new message and stores it into the server list of
        messages given the room name. Broadcast the room and message.
    """
    # import pdb;pdb.set_trace()
    errors = validate_message(data)
    if errors:
        emit("message_failed", errors, broadcast=False)
    timestamp = get_timestamp_trunc()
    user = data['user']
    sender = user
    room_data = ChatRoom.objects.get(id=data['room'])
    room_data.updated_at = datetime.now()
    room_data.save()
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

    # import pdb;pdb.set_trace()
    print(request.sid)
    clients = get_chat_clients(room_data)
    print(clients, 'clientssssssssssssssssss==============$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n\n')
    # import pdb;pdb.set_trace()
    #
    for cl in clients:
        data['client_id'] = cl['user_id']
        emit("message_broadcast", data, broadcast=False, room=cl['sid'])


@socketio.on('online_status')
def online_status(data):
    print('INSIDE ONLINE STATUS -------------------------------------------------------------------------------------')
    rooms = ChatRoom.objects(participants__user_id__contains=data['user_id']).select_related(3)
    online_users = list()
    already_present_user_list = list()
    # import pdb;pdb.set_trace()
    for room in rooms:
        for participant in room.participants:
            for key, value in session.chat_clients.items():
                if str(participant.user_id) == str(value['user']['user_id']):
                    if participant.user_id not in already_present_user_list:
                        online_users.append(participant.to_json())
                        already_present_user_list.append(participant.user_id)
    # print('online_users------====================================', online_users)
    emit("online_status_show", online_users, broadcast=False)


@socketio.on('read_status')
def read_status(data):
    # import pdb;pdb.set_trace()
    print('INSIDE READ STATUS -------------------------------------------------------------------------------------')
    chat_room = ChatRoom.objects(id=data['room']).get()
    if 'message' in data:
        read_message = Message.objects(id=data['message'], recipients__recipient=data['user_id'])
        read_message.update(set__recipients__0__is_read=True)
        read_message.update(set__recipients__1__is_read=True)
    else:
        messages = Message.objects(recipients__room=chat_room, recipients__is_read=False)
        read_message = list()
        # import pdb;pdb.set_trace()

        is_recpt_found = False

        for message in messages:
            for recp in message.recipients:
                if message.sender.user_id != data['user']['user_id']:
                    is_recpt_found = True
            if is_recpt_found:
                message.update(set__recipients__0__is_read=True)
                message.update(set__recipients__1__is_read=True)
                read_message.append(message)
    clients = get_chat_clients(chat_room)
    print(clients, 'clientssssssssssssssssss')
    for cl in clients:
        emit("read_status_show",
             {'data': [message.to_json()['id'] for message in read_message]}, broadcast=False,
             room=cl['sid'])


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

    for participant in room_data.participants:
        print(participant.user_id)
        for key, value in session.chat_clients.items():
            if str(participant.user_id) == value['user']['user_id']:
                clients.append({'sid': key, 'user_id': value['user']['user_id']})
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
