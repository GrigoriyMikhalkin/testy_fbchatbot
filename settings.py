import os

from flask import Flask
from mongoengine import connect


# setting app
app = Flask(__name__)


# setting mongodb connection
connect(host=os.environ.get('MONGODB_URI'))


# setting webhook server
from base.server import WebhookServer
from base.handlers import (
    data_science_message_handler, usd_rub_rate_postback_handler,
    euro_rub_rate_postback_handler, current_weather_message_handler,
    choose_phrase_message_handler, usd_rub_exchange_rate_date_message_handler,
    euro_rub_exchange_rate_date_message_handler
)

server = WebhookServer()

# setting message handlers
server.set_message_handler(data_science_message_handler, "DEFAULT_HANDLER",
                           default=True)
server.set_message_handler(choose_phrase_message_handler,
                           "CHOOSE_PHRASE_HANDLER")
server.set_message_handler(usd_rub_exchange_rate_date_message_handler,
                           "USDRUB_MESSAGE_HANDLER")
server.set_message_handler(euro_rub_exchange_rate_date_message_handler,
                           "EURRUB_MESSAGE_HANDLER")


# setting postback handlers
server.set_postback_handler(usd_rub_rate_postback_handler, "USDRUB_PAYLOAD")
server.set_postback_handler(euro_rub_rate_postback_handler, "EURRUB_PAYLOAD")
server.set_postback_handler(current_weather_message_handler, "WEATHER_PAYLOAD")
