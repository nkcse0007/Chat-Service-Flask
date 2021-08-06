from app import db
from utils.constants import *
from utils.db.base_model import AbstractBaseModel


class ChatUser(db.EmbeddedDocument):
    user_id = db.StringField(required=True)
    email = db.EmailField(required=True)
    name = db.StringField(default='', required=False)
    profile_image = db.URLField(default='https://www.classifapp.com/wp-content/uploads/2017/09/avatar-placeholder.png',
                                required=False)

    def to_json(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'profile_image': self.profile_image
        }


class ChatRoom(AbstractBaseModel):
    creator = db.EmbeddedDocumentField(ChatUser, required=True)
    is_group = db.BooleanField(default=True)
    admins = db.ListField(db.EmbeddedDocumentField(ChatUser, required=True), default=list)
    name = db.StringField(required=True)
    image = db.URLField(required=False)
    status = db.MultiLineStringField(required=False)
    participants = db.ListField(db.EmbeddedDocumentField(ChatUser, required=True), default=list)

    def to_json(self, *args, **kwargs):
        return {
            'id': str(self.pk),
            'creator_id': self.creator.to_json(),
            'is_group': self.is_group,
            'admins': [admin.to_json() for admin in self.admins],
            'name': self.name,
            'image': self.image,
            'status': self.status,
            'participants': [participant.to_json() for participant in self.participants],
            'created_at': self.created_at.timestamp(),
            'updated_at': self.updated_at.timestamp(),
        }


class MessageRecipients(db.EmbeddedDocument):
    recipient = db.EmbeddedDocumentField(ChatUser, required=True)
    room = db.ReferenceField(ChatRoom)
    is_received = db.ListField(db.EmbeddedDocumentField(ChatUser, required=True), default=list)
    is_read = db.ListField(db.EmbeddedDocumentField(ChatUser, required=True), default=list)

    def to_json(self):
        return {
            'recipient': self.recipient.to_json(),
            'is_received': self.is_received,
            'is_read': self.is_read,
            'room': self.room.to_json()
        }


class MessageMedia(db.EmbeddedDocument):
    link = db.URLField(required=False)
    caption = db.StringField(required=False)


class Message(AbstractBaseModel):
    sender = db.EmbeddedDocumentField(ChatUser, required=True)
    type = db.StringField(choices=MESSAGE_TYPES, default=DEFAULT_MESSAGE_TYPE, required=True)
    message_body = db.StringField(required=True)
    message_media = db.EmbeddedDocumentField(MessageMedia)
    is_sent = db.BooleanField(default=False)
    recipients = db.EmbeddedDocumentListField(MessageRecipients)

    def to_json(self, *args, **kwargs):
        return {
            'sender': self.sender.to_json(),
            'type': self.type,
            'message_body': self.message_body,
            'message_media': self.message_media,
            'is_sent': self.is_sent,
            'recipients': [recipient.to_json() for recipient in self.recipients],
            'created_at': self.created_at.timestamp(),
            'updated_at': self.updated_at.timestamp(),
        }
