import os
from datetime import datetime, timedelta
from lxml import etree
import requests

from .models import ExchangeRate, Weather


UPDATE_WEATHER_TIME_GAP = 30  # minutes

EXCHANGE_RATES_URL = 'http://www.cbr.ru/scripts/XML_daily_eng.asp'
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'


# Message handlers
def data_science_message_handler(request):
    # function(request) -> (response, next message handler)
    return "Test!", None


def exchange_rate_date_message_handler(request):
    pass


def current_weather_city_message_handler(request):
    pass


# Postback handlers
def exchange_rate_postback_handler(currency_from, currency_to):
    """
    Get exchange rate for today from cbr.ru

    :param: request: dict
    """
    today = datetime.now().date()
    message = "Курс {cfrom} к {cto} на сегодня: {rate}{cto}"

    # check if exchange rate already in DB
    exchange_rate = ExchangeRate.objects(
        currency_from=currency_from, currency_to=currency_to, date=today
    ).first()
    if exchange_rate:
        message = message.format(cfrom=currency_from, cto=currency_to,
                                 rate=exchange_rate.rate)
        return message, None

    # if not, load data from cbr.ru
    response = requests.get(EXCHANGE_RATES_URL)
    xml = bytes(response.text, encoding='utf-8')
    root = etree.XML(xml)

    xpath = '//Valute[CharCode="{}"]/Value/text()'.format(currency_from)
    rate = root.xpath(xpath)[0]

    exchange_rate = ExchangeRate(
        currency_from=currency_from, currency_to=currency_to, date=today,
        rate=rate
    )
    exchange_rate.save()

    message = message.format(cfrom=currency_from, cto=currency_to, rate=rate)
    return message, None


usd_rub_rate_postback_handler = \
    lambda request: exchange_rate_postback_handler('USD', 'RUB')


euro_rub_rate_postback_handler = \
    lambda request: exchange_rate_postback_handler('EUR', 'RUB')


def current_weather_message_handler(request):
    """
    Get weather data from openweathermap.org

    :param: request: dict
    """
    now = datetime.now()
    time_mark = now - timedelta(minutes=UPDATE_WEATHER_TIME_GAP)
    message = "Москва, Россия. Температура {temp}C. Скорость ветра {ws}м/c."

    # check if there recent weather data in DB
    weather = Weather.objects(city='Moscow', time__gte=time_mark).first()
    if weather:
        message = message.format(temp=weather.temp, ws=weather.wind_speed)
        return message, None

    # if not, load data from
    payload = {'q': 'Moscow', 'units': 'metric',
               'appid': os.environ.get('OWM_APPID')}
    response = requests.get(WEATHER_URL, params=payload)
    data = response.json()
    temp = str(data['main'].get('temp'))
    wind_speed = str(data['wind'].get('speed'))
    weather = Weather(city='Moscow', temp=temp, wind_speed=wind_speed, time=now)
    weather.save()

    message = message.format(temp=temp, ws=wind_speed)
    return message, None
