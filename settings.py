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
    euro_rub_rate_postback_handler, current_weather_message_handler
)

server = WebhookServer()

# setting message handlers
server.set_message_handler(data_science_message_handler, "DEFAULT_HANDLER",
                           default=True)

# setting postback handlers
server.set_postback_handler(usd_rub_rate_postback_handler, "USDRUB_PAYLOAD")
server.set_postback_handler(euro_rub_rate_postback_handler, "EURRUB_PAYLOAD")
server.set_postback_handler(current_weather_message_handler, "WEATHER_PAYLOAD")
