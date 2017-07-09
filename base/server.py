import os
import json

import requests

from .utils import log
from .exceptions import (DuplicateHandlerCodeException,
                         MessageHandlerNotSettedException,
                         PostbackHandlerUndefinedException)
from .models import User, RequestResponse


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
        if message_handler_code is None:
            message_handler_code = self.default_message_handler

        # Check that message handler exists
        message_handler = self.message_handlers.get(message_handler_code, None)
        if message_handler is None:
            raise MessageHandlerNotSettedException

        user = User.objects(user_id=str(user_id)).first()
        if user:
            user.next_handler = message_handler_code
        else:
            user = User(user_id=str(user_id), next_handler=message_handler_code)
        user.save()

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
        user = User.objects(user_id=str(sender_id)).first()
        if user:
            message_handler_code = user.next_handler
        else:
            message_handler_code = self.default_message_handler

        message_handler = self.message_handlers.get(message_handler_code)
        if not message_handler:
            raise MessageHandlerNotSettedException

        reponse_message, next_handler = message_handler(message)

        # Save request and response
        response_request = RequestResponse(
            user_id=str(sender_id), request_type='message',
            request_message=message, response_text=reponse_message
        )
        response_request.save()

        self.switch_user_message_handler(sender_id, next_handler)
        self.send_message(sender_id, reponse_message)

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

        # Save request and response
        response_request = RequestResponse(
            user_id=str(sender_id), request_type='postback',
            postback_type=postback_code, response_text=message
        )
        response_request.save()

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
