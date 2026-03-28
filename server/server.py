import asyncio
from http.client import responses

from aiohttp import web
from pathlib import Path
import json
import opcodes
import random

from web_socket_wrapper import WebSocketWrapper

STATIC_DIR = "../client"
web_socket_wrappers_array = []
words = ["cat", "dog", "bomb", "egg", "love"]

# --- HTTP handler ---
async def http_handler(request):
    return web.Response(text="Hello from HTTP!")

async def index(request):
    content = open(f"{STATIC_DIR}/Scribble.html", "rt").read()
    return web.Response(text=content, content_type="text/html")

async def handle_user_message(source_wrapper:WebSocketWrapper, user_message: dict) -> dict:
    print(user_message)
    opcode = user_message['opcode']

    # await ws.send_str(f"opcode: {opcodes.server_2_client['Connection Established']}, message: Connection Established")
    #
    if opcode == opcodes.client_2_server['login']:
        source_wrapper.params['username'] = user_message['src']
        source_wrapper.params['id'] = user_message['id']

        return {
            'opcode': opcodes.server_2_client["Connection Established"],
            'message': "connection established",
            'src': user_message['src']
        }

    elif opcode == opcodes.client_2_server['Message sent']:
        return {
            'opcode': opcodes.server_2_client['Message sent'],
            'message': user_message['message'],
            'src': source_wrapper.params['username'],
            'id': source_wrapper.params['id']
        }

    elif opcode == opcodes.client_2_server['Ping']:
        return {
            'opcode': opcodes.server_2_client['Pong'],
            'message': "pong",
            'src': source_wrapper.params['username']
        }

    elif opcode == opcodes.client_2_server['Draw']:
        return {
            'opcode': opcodes.server_2_client['Draw'],
            'message': user_message['message'],
            'src': source_wrapper.params['username']
        }

    elif opcode == opcodes.client_2_server['Delete canvas']:
        return {
            'opcode': opcodes.server_2_client['Delete canvas'],
            'message': user_message['message'],
            'src': source_wrapper.params['username']
        }

    elif opcode == opcodes.client_2_server['I am current player']:
        return {
            'opcode': opcodes.server_2_client['There is a new current player'],
            'message': source_wrapper.params['username'] + " is the current player",
            'src': "server",
            'id': source_wrapper.params['id']
        }

    elif opcode == opcodes.client_2_server['Request word']:
        word = random.choice(words)
        return {
            'opcode': opcodes.server_2_client['You got a word'],
            'message': word,
            'src': "server"
        }

    elif opcode == 30:
        return {'opcode': 1,
                'message': "crap"}

    else:
        return {'opcode': "unknown"}

# --- WebSocket handler ---
async def websocket_handler(request):
    global web_socket_wrappers_array
    ws = web.WebSocketResponse()
    wrapper = WebSocketWrapper(ws, {})
    web_socket_wrappers_array.append(wrapper)
    await ws.prepare(request)

    print("WebSocket connected")

    # for player in web_sockets_array:
    #     current_word = random.choice(words)
    #     for dst in web_sockets_array:
    #
    #         if dst != player:
    #             response_as_str = json.dumps({
    #                 "opcode": opcodes.server_2_client["Word was chosen"],
    #                 "message": "A word was chosen",
    #                 "src": "server",
    #             })
    #             await dst.send_str(response_as_str)
    #
    #         elif dst == player:
    #             response_as_str = json.dumps({
    #                 "opcode": opcodes.server_2_client["Word was chosen"],
    #                 "message": current_word,
    #                 "src": "server",
    #             })
    #             await dst.send_str(response_as_str)


    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            user_message_as_dict = json.loads(msg.data)

            response_as_dict = await handle_user_message(wrapper, user_message_as_dict)
            # if response_as_dict["message"] == current_word:
            #     response_as_dict["message"] = response_as_dict["src"] + " has found the word"
            response_as_str = json.dumps(response_as_dict)
            print(response_as_str)
            if user_message_as_dict['dst'] == "broadcast":
                await broadcast_message(response_as_str)

            elif user_message_as_dict['dst'] == "server":
                await send_message_to_player_wrapper(response_as_str, wrapper)


        elif msg.type == web.WSMsgType.ERROR:
            print("WebSocket error:", ws.exception())

    print("WebSocket closed")
    web_socket_wrappers_array.remove(wrapper)
    return ws

async def broadcast_message(message):
    global web_socket_wrappers_array
    for dst in web_socket_wrappers_array:
        await dst.ws.send_str(message)

async def send_message_to_player_name(message, player_name: str):
    ws_wrapper = find_ws_from_username(player_name)
    await ws_wrapper.ws.send_str(message)

async def send_message_to_player_wrapper(message, wrapper):
    await wrapper.ws.send_str(message)

def find_ws_from_username(username):
    global web_socket_wrappers_array
    for wrapper in web_socket_wrappers_array:
        if wrapper.params.username == username:
            return wrapper

    return None

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
