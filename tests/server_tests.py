import os
import json
import unittest
from unittest.mock import patch, Mock

from base.exceptions import (DuplicateHandlerCodeException,
                             MessageHandlerNotSettedException,
                             PostbackHandlerUndefinedException)
from base.server import WebhookServer, MESSAGES_POST_LINK

from .test_utils import set_env_variable


class WebhookServerTestCase(unittest.TestCase):

    def setUp(self):
        self.server = WebhookServer()
        self.server.set_message_handler(self.message_handler, "special_handler")

    def message_handler(self, request):
        return "received", "special_handler"

    def test_set_message_handler(self):
        handler_code1 = "handler1"
        handler_code2 = "handler2"

        # add new handler
        self.server.set_message_handler(self.message_handler, handler_code1)
        self.assertEqual(len(self.server.message_handlers), 2)
        self.assertIn(handler_code1, self.server.message_handlers)
        self.assertIsNone(self.server.default_message_handler)

        # add handler with existing handler code
        self.assertRaises(
            DuplicateHandlerCodeException, self.server.set_message_handler,
            self.message_handler, handler_code1
        )

        # add handler as default
        self.server.set_message_handler(self.message_handler, handler_code2,
                                        default=True)
        self.assertEqual(len(self.server.message_handlers), 3)
        self.assertIn(handler_code2, self.server.message_handlers)
        self.assertEqual(handler_code2,
                         self.server.default_message_handler)

    def test_set_postback_handler(self):
        handler_code = "handler"

        # add new handler
        self.server.set_postback_handler(self.message_handler, handler_code)
        self.assertEqual(len(self.server.postback_handlers), 1)
        self.assertIn(handler_code, self.server.postback_handlers)

        # add handler with existing handler code
        self.assertRaises(
            DuplicateHandlerCodeException, self.server.set_postback_handler,
            self.message_handler, handler_code
        )

    def test_switch_user_message_handler(self):
        user_id = 1
        handler_code1 = "handler1"
        handler_code2 = "handler2"
        self.server.set_message_handler(self.message_handler, handler_code1,
                                        default=True)

        # handler is not setted
        self.assertRaises(
            MessageHandlerNotSettedException,
            self.server.switch_user_message_handler, user_id, handler_code2
        )

        # set special handler for user
        self.server.set_message_handler(self.message_handler, handler_code2)
        self.server.switch_user_message_handler(user_id, handler_code2)
        self.assertEqual(self.server.special_handler_mapper[user_id],
                         handler_code2)

        # set default handler for user
        self.server.switch_user_message_handler(user_id, None)
        self.assertIsNone(self.server.special_handler_mapper.get(user_id))

    @set_env_variable('PAGE_ACCESS_TOKEN', 'test')
    @patch('base.server.requests')
    def test_send_message(self, mock_obj):
        recipient_id = 1
        message_text = "test"
        response_mock = Mock()
        response_mock.status_code = 200
        mock_obj.post.return_value = response_mock
        expected_params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
        expected_headers = {"Content-Type": "application/json"}
        expected_data = json.dumps({
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        })

        self.server.send_message(recipient_id, message_text)
        mock_obj.post.assert_called_with(
            MESSAGES_POST_LINK, params=expected_params, headers=expected_headers,
            data=expected_data
        )

    @set_env_variable('PAGE_ACCESS_TOKEN', 'test')
    @patch('base.server.requests')
    def test_handle_message(self, mock_obj):
        message = "test"
        sender_id = 1
        handler_code = "handler"

        # message handler not setted up
        self.assertRaises(
            MessageHandlerNotSettedException,
            self.server.handle_message, message, sender_id
        )

        # handle message
        self.server.set_message_handler(self.message_handler, handler_code,
                                        default=True)
        self.server.handle_message(message, sender_id)
        self.assertEqual(self.server.special_handler_mapper[sender_id],
                         "special_handler")

    @set_env_variable('PAGE_ACCESS_TOKEN', 'test')
    @patch('base.server.requests')
    def test_handle_postback(self, mock_obj):
        handler_code = "handler"
        sender_id = 1
        postback = {"payload": handler_code}

        # message handler not setted up
        self.assertRaises(
            PostbackHandlerUndefinedException,
            self.server.handle_postback, postback, sender_id
        )

        # handle message
        self.server.set_postback_handler(self.message_handler, handler_code)
        self.server.handle_postback(postback, sender_id)
        self.assertEqual(self.server.special_handler_mapper[sender_id],
                         "special_handler")

    @set_env_variable('PAGE_ACCESS_TOKEN', 'test')
    @patch('base.server.requests')
    def test_handle_request(self, mock_obj):
        pass
