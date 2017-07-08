# Message handlers
def data_science_message_handler(request):
    # function(request) -> (response, next message handler)
    return "Test!", None


def exchange_rate_date_message_handler(request):
    pass


def current_weather_city_message_handler(request):
    pass


# Postback handlers
def exchange_rate_postback_handler(request):
    pass


def current_weather_message_handler(request):
    pass
