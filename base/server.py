class WebhookServer:

    def __init__(self):
        self.message_handlers = dict()
        self.postback_handlers = dict()

        self.current_message_handler = None

    def switch_message_handler(self, message_handler_code):
        """
        Set current message handler to message handler
        with provided message handler code

        :param: message_handler_code: str
        """
        pass

    def set_message_handler(self, handler):
        """
        Set message handler

        :param: handler: function(request) -> (response, next message handler)
        """
        pass

    def set_postback_handler(self, handler):
        """
        Set postback handler

        :param: handler: function(requst) -> (response, next message handler)
        """
        pass

    def run(self):
        """
        Run server to listen for hooks
        """
