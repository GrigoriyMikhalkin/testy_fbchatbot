from flask import Flask, request

from base.server import WebhookServer
from base.handlers import data_science_message_handler


app = Flask(__name__)
server = WebhookServer()
server.set_message_handler(data_science_message_handler,
                           "DEFAULT_HANDLER", default=True)


@app.route('/', methods=['GET'])
def verify():
    """
    When the endpoint is registered as a webhook, it must echo back
    the 'hub.challenge' value it receives in the query arguments
    """
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def listen():
    return server.handle_request(request)

if __name__ == '__main__':
    app.run(debug=True)
