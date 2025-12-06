from http.client import responses

from aiohttp import web
from pathlib import Path
import json

STATIC_DIR = "../client"

# --- HTTP handler ---
async def http_handler(request):
    return web.Response(text="Hello from HTTP!")

async def index(request):
    content = open(f"{STATIC_DIR}/Scribble.html", "rt").read()
    return web.Response(text=content, content_type="text/html")

async def handle_user_message(user_message: dict) -> dict:
    print(user_message)
    opcode = user_message['opcode']
    if opcode == 0:
        return {'opcode': 1, 'message': 3}
    elif opcode == 6:
        return {'opcode': 1, 'message': "crap"}
    return {'opcode': "unknown"}

# --- WebSocket handler ---
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("WebSocket connected")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            user_message_as_dict = json.loads(msg.data)
            response_as_dict = await handle_user_message(user_message_as_dict)
            response_as_str = json.dumps(response_as_dict)
            await ws.send_str(response_as_str)

        elif msg.type == web.WSMsgType.ERROR:
            print("WebSocket error:", ws.exception())

    print("WebSocket closed")
    return ws

def main():
    # --- App setup ---
    app = web.Application()
    # app.router.add_get("/", http_handler)          # HTTP endpoint
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)   # WebSocket endpoint
    app.router.add_static("/", path="../client")

    # Run BOTH on the same server + port
    web.run_app(app, host="localhost", port=8080)


if __name__ == "__main__":
    main()
