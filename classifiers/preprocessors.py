import re


def preprocessor(row_string):
    processed_string = re.sub('[^а-яА-Яa-zA-Z]', ' ', row_string)
    return processed_string
