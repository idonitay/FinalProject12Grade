from aiohttp.web_ws import WebSocketResponse


class WebSocketWrapper:
    def __init__(self, ws:WebSocketResponse):
        self.ws = ws
        self.username = ""
        self.id = ""
        self.answered = False
        self.current_player = False