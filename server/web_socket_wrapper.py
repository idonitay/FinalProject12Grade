from aiohttp.web_ws import WebSocketResponse


class WebSocketWrapper:
    def __init__(self, ws:WebSocketResponse, params: dict):
        self.ws = ws
        self.params = params