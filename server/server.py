from aiohttp import web
from pathlib import Path

STATIC_DIR = "../client"

# --- HTTP handler ---
async def http_handler(request):
    return web.Response(text="Hello from HTTP!")

async def index(request):
    content = open(f"{STATIC_DIR}/Scribble.html", "rt").read()
    return web.Response(text=content, content_type="text/html")

# --- WebSocket handler ---
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("WebSocket connected")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            print("WS message:", msg.data)
            await ws.send_str(f"You said: {msg.data}")
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
