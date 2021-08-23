# flask packages
from flask import Flask, app
from flask_restful import Api
from flask_mongoengine import MongoEngine
import os
from flask_mail import Mail
from socketsio import create_socketio, socketio
from flask_cors import CORS
from flask_session import Session
import logging
import urllib

# init mongoengine
db = MongoEngine()
session = Session()

session.chat_clients = {}

# init flask mail
mail = Mail()

from dotenv import load_dotenv

load_dotenv()

# default mongodb configuration
default_config = {
    'MONGODB_SETTINGS': {
        'db': os.environ['DB_NAME'],
        'host': os.environ['DB_HOST'],
        'port': int(os.environ['DB_PORT']),
        'username': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'authentication_source': 'admin'
    },
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 465,
    'MAIL_USERNAME': 'nkcse0007@gmail.com',
    'MAIL_PASSWORD': 'Bond007@#1996',
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': True,
    'SECRET_KEY': os.environ.get('SECRET_KEY'),
    "SESSION_PERMANENT": False,
    "SESSION_TYPE": "filesystem",
    'CORS_HEADERS': 'Content-Type',
    'CORS_ALLOW_HEADERS': "*",
    'CORS_ALWAYS_SEND': True,
    'CORS_AUTOMATIC_OPTIONS': True,
    'CORS_EXPOSE_HEADERS': None,
    'CORS_INTERCEPT_EXCEPTIONS': True,
    'CORS_MAX_AGE': None,
    'CORS_METHODS': ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
    'CORS_ORIGINS': "*",
    'CORS_RESOURCES': r"/*",
    'CORS_SEND_WILDCARD': False,
    'CORS_SUPPORTS_CREDENTIALS': False,
    'CORS_VARY_HEADER': True,
}


def get_flask_app(config: dict = None) -> app.Flask:
    """
    Initializes Flask app with given configuration.
    Main entry point for wsgi (gunicorn) server.
    :param config: Configuration dictionary
    :return: app
    """
    # init flask
    flask_app = Flask(__name__)
    CORS(flask_app, resources={r"/*": {"origins": "*"}})

    # configure app
    config = default_config if config is None else config
    flask_app.config.update(config)

    # load config variables
#    if 'MONGODB_URI' in os.environ:
#    flask_app.config['MONGODB_SETTINGS'] = {'host': f"mongodb+srv://dliff:{urllib.parse.quote('dliff@123')}@cluster0.mvxi2.mongodb.net/Dliff?retryWrites=true&w=majority",
#                                                'retryWrites': False}

    # init api and routes
    api = Api(app=flask_app)
    from chat.routes import create_chat_routes
    create_chat_routes(api=api)
    db.init_app(flask_app)

    mail.init_app(flask_app)

    session.init_app(flask_app)

    return flask_app


if __name__ == '__main__':
    # Main entry point when run in stand-alone mode.
    app = get_flask_app()
    create_socketio(app)
    socketio.run(app, host=os.environ.get('HOST'), port=os.environ.get('PORT'), debug=True)
