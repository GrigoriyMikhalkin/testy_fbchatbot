import os
import json

import requests

from .utils import log
from .exceptions import (DuplicateHandlerCodeException,
                         MessageHandlerNotSettedException,
                         PostbackHandlerUndefinedException)


# Constants
MESSAGES_POST_LINK = "https://graph.facebook.com/v2.6/me/messages"


class WebhookServer:
    """
    Webhook server that listens to requests from Facebook messenger
    """

    def __init__(self):
        self.message_handlers = dict()
        self.postback_handlers = dict()

        self.default_message_handler = None

        # if sender needs special message handler
        # then we store his id in mapper
        self.special_handler_mapper = dict()

    def set_message_handler(self, handler, handler_code, default=False):
        """
        Set message handler

        :param: handler: function(message) -> (response, next message handler)
        :param: handler_code: str
        :param: default: bool: set handler as default message handler
        """
        if handler_code in self.message_handlers:
            raise DuplicateHandlerCodeException(
                "Message handler with code '%s' already exists" % handler_code
            )

        self.message_handlers[handler_code] = handler
        if default:
            self.default_message_handler = handler_code

    def set_postback_handler(self, handler, handler_code):
        """
        Set postback handler

        :param: handler: function(message) -> (response, next message handler)
        :param: handler_code: str
        """
        if handler_code in self.postback_handlers:
            raise DuplicateHandlerCodeException(
                "Postback handler with code '%s' already exists" % handler_code
            )

        self.postback_handlers[handler_code] = handler

    def switch_user_message_handler(self, user_id, message_handler_code):
        """
        Update user to message handler mapping

        :param: user_id: int
        :param: message_handler_code: str
        """
        if message_handler_code is None or \
            message_handler_code == self.default_message_handler:
            if user_id in self.special_handler_mapper:
                del self.special_handler_mapper[user_id]
            return

        message_handler = self.message_handlers.get(message_handler_code, None)
        if message_handler is None:
            raise MessageHandlerNotSettedException

        self.special_handler_mapper[user_id] = message_handler_code

    def send_message(self, recipient_id, message_text):
        """
        Send message to recipient

        :param: recipient_id: int
        :param: message_text: str
        """
        log("sending message to {recipient}: {text}".format(
            recipient=recipient_id, text=message_text))

        params = {
            "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        })

        r = requests.post(MESSAGES_POST_LINK,
                          params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)

    def handle_message(self, message, sender_id):
        """
        Handle a message

        :param: message: dict
        :param: sender_id: int
        """
        message_handler_code = self.special_handler_mapper.get(sender_id) or \
            self.default_message_handler
        message_handler = self.message_handlers.get(message_handler_code)
        if not message_handler:
            raise MessageHandlerNotSettedException

        message, next_handler = message_handler(message)

        self.switch_user_message_handler(sender_id, next_handler)
        self.send_message(sender_id, message)

    def handle_postback(self, postback, sender_id):
        """
        Handle a postback

        :param: postback: dict
        :param: sender_id: int
        """
        postback_code = postback.get('payload')
        postback_handler = self.postback_handlers.get(postback_code)
        if not postback_handler:
            raise PostbackHandlerUndefinedException

        message, next_message_handler = postback_handler(postback)

        self.switch_user_message_handler(sender_id, next_message_handler)
        self.send_message(sender_id, message)

    def handle_request(self, request):
        """
        Dispatch request to right handler
        and set message handler to handle next message request
        """
        data = request.get_json()
        log(data)

        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    try:
                        sender_id = messaging_event["sender"]["id"]

                        # handling a message
                        message = messaging_event.get("message", None)
                        if message is not None:
                            self.handle_message(message, sender_id)

                        # handling a postback
                        postback = messaging_event.get("postback", None)
                        if postback is not None:
                            self.handle_postback(postback, sender_id)
                    except Exception as exc:
                        log(exc)

        return "ok", 200
