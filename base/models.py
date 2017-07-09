import datetime

from mongoengine import *


# Fields
class DateField(DateTimeField):
    """
    Date field based on DateTimeField,
    have strict check that value is datetime.date instance
    """
    def validate(self, value):
        if not isinstance(value, datetime.date):
            self.error("cannot parse date %s" % value)
        super().validate(value)


# Models
class User(Document):
    user_id = StringField(required=True)
    next_handler = StringField(required=True)


class RequestResponse(Document):
    user_id = StringField(required=True)
    request_type = StringField(required=True)
    request_message = StringField(null=True)
    postback_type = StringField(null=True)
    response_text = StringField(required=True)


class ExchangeRate(Document):
    currency_from = StringField(required=True)
    currency_to = StringField(required=True)
    rate = StringField(required=True)
    date = DateField(required=True)


class Weather(Document):
    city = StringField(required=True)
    temp = StringField(required=True)
    wind_speed = StringField(required=True)
    time = DateTimeField(required=True)
