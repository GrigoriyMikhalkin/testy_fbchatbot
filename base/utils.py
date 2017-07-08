import sys


def log(message):
    """
    Simple wrapper for logging to stdout on heroku

    :param: message: str
    """
    print(str(message))
    sys.stdout.flush()
