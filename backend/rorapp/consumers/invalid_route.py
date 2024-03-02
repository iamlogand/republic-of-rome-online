from channels.generic.websocket import WebsocketConsumer


# Closes the connection. Used as a catch-all pattern for invalid routes.
class InvalidRouteConsumer(WebsocketConsumer):
    def connect(self):
        self.close()
