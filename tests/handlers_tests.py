import os
import json
import unittest
from datetime import datetime
from unittest.mock import patch, Mock

import responses
from mongoengine import connect

from base.server import WebhookServer, MESSAGES_POST_LINK
from base.handlers import (usd_rub_rate_postback_handler, EXCHANGE_RATES_URL,
                           usd_rub_exchange_rate_date_message_handler,
                           current_weather_message_handler, WEATHER_URL,
                           UPDATE_WEATHER_TIME_GAP)
from base.models import ExchangeRate, Weather
from .test_utils import set_env_variable


class HandlersTestCase(unittest.TestCase):

    def setUp(self):
        self.db = connect(host=os.environ.get('MONGODB_TEST_HOST') + \
                          os.environ.get('MONGODB_TEST_NAME'))
        self.server = WebhookServer()
        self.server.set_message_handler(self.message_handler, "handler",
                                        default=True)

    def tearDown(self):
        self.db.drop_database(os.environ.get('MONGODB_TEST_NAME'))

    def message_handler(self, request):
        return 'Test', None

    @set_env_variable('PAGE_ACCESS_TOKEN', 'test')
    def test_exchange_rate_postback_handler(self):
        today = datetime.now().date()
        handler_code = 'exchange_rate_handler'
        exchange_message_handler = 'USDRUB_MESSAGE_HANDLER'

        self.server.set_message_handler(
            usd_rub_exchange_rate_date_message_handler,
             exchange_message_handler
        )
        self.server.set_postback_handler(usd_rub_rate_postback_handler,
                                         handler_code)

        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, MESSAGES_POST_LINK, status=200)
            self.server.handle_postback({'payload': handler_code}, 1)

            # db is empty
            body = '<ValCurs><Valute>' +\
                   '<CharCode>USD</CharCode>' +\
                   '<Value>100500,000</Value>' +\
                   '</Valute></ValCurs>'
            rsps.add(responses.GET, EXCHANGE_RATES_URL, body=body)
            rsps.add(responses.POST, MESSAGES_POST_LINK, status=200)
            self.server.handle_message({'text': 'test'}, 1)
            self.assertEqual(ExchangeRate.objects.count(), 1)
            self.assertEqual(ExchangeRate.objects(date=today).first().rate,
                             '100500,000')

            # today's rate in db
            rsps.add(responses.POST, MESSAGES_POST_LINK, status=200)
            self.server.handle_message({'text': 'сегодня'}, 1)
            self.assertEqual(ExchangeRate.objects.count(), 1)

    @set_env_variable('PAGE_ACCESS_TOKEN', 'test')
    def test_current_weather_message_handler(self):
        now = datetime.now()
        handler_code = 'weather_handler'
        self.server.set_postback_handler(current_weather_message_handler,
                                         handler_code)

        with responses.RequestsMock() as rsps:
            # db is empty
            body = {'main': {'temp': 20.6}, 'wind': {'speed': 6}}
            body_str = json.dumps(body)
            rsps.add(responses.GET, WEATHER_URL, body=body_str)
            rsps.add(responses.POST, MESSAGES_POST_LINK, status=200)
            self.server.handle_postback({'payload': handler_code}, 1)
            self.assertEqual(Weather.objects.count(), 1)
            self.assertEqual(Weather.objects().first().temp, '20.6')
            self.assertEqual(Weather.objects().first().wind_speed, '6')

            # recent weather data in db
            rsps.add(responses.POST, MESSAGES_POST_LINK, status=200)
            self.server.handle_postback({'payload': handler_code}, 1)
            self.assertEqual(Weather.objects.count(), 1)
