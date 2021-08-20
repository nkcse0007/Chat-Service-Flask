from flask_restful import Api

# project resources
from chat.views import ChatApi, MessageApi


def create_chat_routes(api: Api):
    """Adds resources to the api.

    :param api: Flask-RESTful Api Object

    :Example:

        api.add_resource(HelloWorld, '/', '/hello')
        api.add_resource(Foo, '/foo', endpoint="foo")
        api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

    """
    api.add_resource(ChatApi, '/chat/')
    api.add_resource(MessageApi, '/chat/message/')
