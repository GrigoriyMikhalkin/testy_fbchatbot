import os
from datetime import datetime, timedelta
from lxml import etree
import requests

import pymorphy2
from sklearn.externals import joblib

from classifiers.preprocessors import normalizing_preprocessor
from .models import ExchangeRate, Weather
from .utils import log


GLOSSARY_PATH = '.data/data_science_glossary'
GLOSSARY = None

CLASSIFIER_PATH = './data/forest.pkl'
VECTORIZER_PATH = './data/vectorizer.pkl'
classifier = joblib.load(CLASSIFIER_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

UPDATE_WEATHER_TIME_GAP = 30  # minutes

EXCHANGE_RATES_URL = 'http://www.cbr.ru/scripts/XML_daily_eng.asp'
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'


def load_data_science_glossary():
    """
    Load and process data science glossary from file
    """
    global GLOSSARY
    with open(GLOSSARY_PATH, 'r') as f_glossary:
        GLOSSARY = dict()
        for line in f_glossary.readlines():
            line = line.strip()
            processed_line = normalizing_preprocessor(line)
            GLOSSARY[line] = processed_line


def search_for_key_noun_phrases(text):
    """
    Searching if phrases from glossary found in text

    :param: text: str
    :return: list: list of found phrases
    """
    if GLOSSARY is None:
        load_data_science_glossary()

    phrases = []
    normalized_text = normalizing_preprocessor(text)

    for phrase, norm_phrase in GLOSSARY.items():
        if norm_phrase in normalized_text:
            phrases.append(phrase)

    return phrases


def create_message_about_data_science(phrases):
    """
    Creates new message based on found phrases

    :param: phrases: list
    :return: (str, str): Pair of message and next handler code
    """
    next_handler = None

    if len(phrases) == 0:
        message = "Вас интересует Data Science? " +\
                  "К сожалению, не могу ответить на вопрос детальнее." +\
                  "Вот ссылка на статью, про data science, в вики: " +\
                  "https://ru.wikipedia.org/wiki/Data_science"

    elif len(phrases) == 1:
        phrase = phrases[0]
        message = "Вас интересует {phrase}?" +\
                  "Вот ссылка на статью про {phrase} в вики: " +\
                  "https://ru.wikipedia.org/wiki/{und_phrase}".format(
                    phrase=phrase, und_phrases=phrase.replace(' ', '_')
                  )
    else:
        phrases_str = ', '.join(phrases)
        message = "Вас интересует одна из этих тем: {phrases}?" +\
                  "Какая именно?".format(phrases=phrases_str)
        next_handler = 'CHOOSE_PHRASE_HANDLER'

    return message, next_handler


# Message handlers
def data_science_message_handler(request):
    """
    Classifies user's message and if it's topic is data science
    tries to find more specific subject user is interested in
    and give link to wiki page on it

    :param: request: dict
    """
    next_handler = None
    text = request.get('text')
    text_features = vectorizer.transform([text])
    result = classifier.predict(text_features)[0]

    if result == '1':
        phrases = search_for_key_noun_phrases(text)
        message, next_handler = create_message_about_data_science(phrases)

    else:
        message = "Ничего не могу сказать на эту тему."

    return message, next_handler


def choose_phrase_message_handler(request):
    """
    Determine in which data science topic user is interested

    :prama: request: dict
    """
    text = request.get('text')
    phrases = search_for_key_noun_phrases(text)
    message, handler = create_message_about_data_science(phrases)

    return message, handler


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

    if response.status_code != 200:
        log(response.status_code)
        log(os.environ.get('OWM_APPID'))
    data = response.json()

    temp = str(data['main'].get('temp'))
    wind_speed = str(data['wind'].get('speed'))
    weather = Weather(city='Moscow', temp=temp, wind_speed=wind_speed, time=now)
    weather.save()

    message = message.format(temp=temp, ws=wind_speed)
    return message, None
