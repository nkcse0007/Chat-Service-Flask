from flask import render_template, make_response
from flask_restful import Resource
from flask import request, jsonify
from .selectors import get_rooms, get_messages


class ChatApi(Resource):

    @staticmethod
    def get():
        input_data = request.values.to_dict()
        return make_response(render_template("index.html",
                                             # users=users,
                                             channels=[]))


class MessageApi(Resource):

    @staticmethod
    def get():
        input_data = request.values.to_dict()
        response = get_messages(input_data)
        return jsonify(response)
