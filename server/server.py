import asyncio
from http.client import responses

from aiohttp import web
from pathlib import Path
import json

#from mysql.connector.django.base import adapt_datetime_with_timezone_support

import opcodes
import random
import hashlib
import hmac
from db_conn import get_words_from_db

from web_socket_wrapper import WebSocketWrapper
from encryption_decryption import encrypt_message
from encryption_decryption import decrypt_message

STATIC_DIR = "../client"
web_socket_wrappers_array = []
words = get_words_from_db()
word = ""
duration = 60  # seconds
end_time = 0

# --- HTTP handler ---
async def http_handler(request):
    return web.Response(text="Hello from HTTP!")

async def index(request):
    content = open(f"{STATIC_DIR}/Scribble.html", "rt").read()
    return web.Response(text=content, content_type="text/html")

async def handle_user_message(source_wrapper:WebSocketWrapper, user_message: dict) -> dict:
    print(user_message)

    opcode = user_message['opcode']
    global word

    # await ws.send_str(f"opcode: {opcodes.server_2_client['Connection Established']}, message: Connection Established")
    #
    if opcode == opcodes.client_2_server['login']:
        source_wrapper.username = user_message['src']
        source_wrapper.id = user_message['id']

        return {
            'opcode': opcodes.server_2_client["Connection Established"],
            'message': "connection established",
            'src': user_message['src']
        }

    elif opcode == opcodes.client_2_server['Message sent']:
        hash1 = hashlib.sha256(user_message["message"].encode()).digest()
        hash2 = hashlib.sha256(word.encode()).digest()
        if hmac.compare_digest(hash1, hash2):
            if source_wrapper.answered == False:
                source_wrapper.score += 100
                index = find_index_based_on_ws(source_wrapper)
                await send_updated_score_message(index, source_wrapper.score, source_wrapper.username)

            source_wrapper.answered = True
            if source_wrapper.current_player == False:
                return {
                    'opcode': opcodes.server_2_client["A word was guessed"],
                    'message': source_wrapper.username + " has guessed the word correctly",
                    'src': "server",
                    'id': source_wrapper.id
                    }

            return {}

        else:
            return {
                'opcode': opcodes.server_2_client['Message sent'],
                'message': user_message['message'],
                'src': source_wrapper.username,
                'id': source_wrapper.id
            }

    elif opcode == opcodes.client_2_server['Ping']:
        return {
            'opcode': opcodes.server_2_client['Pong'],
            'message': "pong",
            'src': source_wrapper.username
        }

    elif opcode == opcodes.client_2_server['Draw']:
        return {
            'opcode': opcodes.server_2_client['Draw'],
            'message': user_message['message'],
            'src': source_wrapper.username
        }

    elif opcode == opcodes.client_2_server['Delete canvas']:
        return {
            'opcode': opcodes.server_2_client['Delete canvas'],
            'message': user_message['message'],
            'src': source_wrapper.username
        }

    elif opcode == opcodes.client_2_server['I am current player']:
        source_wrapper.current_player = True
        source_wrapper.answered = True
        await send_start_timer_message(60)
        return {
            'opcode': opcodes.server_2_client['There is a new current player'],
            'message': source_wrapper.username + " is the current player",
            'src': "server",
            'id': source_wrapper.id
        }

    elif opcode == opcodes.client_2_server['Request word']:
        word = random.choice(words)
        return {
            'opcode': opcodes.server_2_client['You got a word'],
            'message': word,
            'src': "server"
        }

    elif opcode == opcodes.client_2_server['Timer ended']:
        if source_wrapper.current_player:
            await finish_turn()

        return {}

    elif opcode == opcodes.client_2_server['Change username']:
        source_wrapper.username = user_message['message'];
        return {}


    elif opcode == 30:
        return {'opcode': 1,
                'message': "crap"}

    else:
        return {'opcode': "unknown"}



def check_if_everyone_answered():
    global web_socket_wrappers_array
    for wrapper in web_socket_wrappers_array:
        if not wrapper.answered:
            return False

    return True

def reset_answered():
    global web_socket_wrappers_array
    for wrapper in web_socket_wrappers_array:
        wrapper.answered = False

async def choose_next_player():
    global web_socket_wrappers_array
    global words
    global word

    current_player_index = 0
    for i in range(0, len(web_socket_wrappers_array)):
        if web_socket_wrappers_array[i].current_player:
            current_player_index = i
            break

    web_socket_wrappers_array[current_player_index].current_player = False
    new_player_index = (current_player_index + 1) % len(web_socket_wrappers_array)
    web_socket_wrappers_array[new_player_index].current_player = True
    web_socket_wrappers_array[new_player_index].answered = True


    message_to_players = {
            'opcode': opcodes.server_2_client['There is a new current player'],
            'message': web_socket_wrappers_array[new_player_index].username + " is the current player",
            'src': "server",
            'id': web_socket_wrappers_array[new_player_index].id
        }

    await broadcast_message(message_to_players)


    word = random.choice(words)
    new_word_message = {
            'opcode': opcodes.server_2_client['You got a word'],
            'message': word,
            'src': "server"
        }
    await send_message_to_player_wrapper(new_word_message, web_socket_wrappers_array[new_player_index])


# --- WebSocket handler ---
async def websocket_handler(request):
    global web_socket_wrappers_array
    ws = web.WebSocketResponse()
    wrapper = WebSocketWrapper(ws)
    web_socket_wrappers_array.append(wrapper)
    await ws.prepare(request)

    print("WebSocket connected")


    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:

            payload = json.loads(msg.data)

            # 2. Access the keys from the dictionary
            decrypted = decrypt_message(
                payload["iv"],
                payload["data"]
            )

            user_message_as_dict = json.loads(decrypted)

            response_as_dict = await handle_user_message(wrapper, user_message_as_dict)
            # if response_as_dict["message"] == current_word:
            #     response_as_dict["message"] = response_as_dict["src"] + " has found the word"
            print(response_as_dict)
            if user_message_as_dict['dst'] == "broadcast":
                await broadcast_message(response_as_dict)

            elif user_message_as_dict['dst'] == "server":
                await send_message_to_player_wrapper(response_as_dict, wrapper)

            if check_if_everyone_answered():
                await finish_turn()

        elif msg.type == web.WSMsgType.ERROR:
            print("WebSocket error:", ws.exception())

    print("WebSocket closed")
    web_socket_wrappers_array.remove(wrapper)
    return ws

async def finish_turn() -> None:
    reset_answered()
    message_to_players = {
        'opcode': opcodes.server_2_client['Reveal word'],
        'message': "The word was " + word,
        'src': "server",
    }
    await broadcast_message(message_to_players)
    await choose_next_player()
    await send_start_timer_message(60)


async def send_start_timer_message(time: int):
    message_to_players = {
        'opcode': opcodes.server_2_client['Start timer'],
        'message': '',
        'duration': time,
        'src': "server",
    }

    await broadcast_message(message_to_players)

async def send_updated_score_message(i: int, score: int, player_name: str):
    message_to_players = {
        'opcode': opcodes.server_2_client['Update score'],
        'score': score,
        'index': i,
        'player_name': player_name,
        'src': "server",
    }

    await broadcast_message(message_to_players)


def find_index_based_on_ws(ws: WebSocketWrapper) -> int:
    global web_socket_wrappers_array
    for i in range (0, len(web_socket_wrappers_array)):
        if web_socket_wrappers_array[i] == ws:
            return i

    return -1

async def broadcast_message(message_dict: dict):
    global web_socket_wrappers_array

    # 1. Convert the original message dictionary to a string
    raw_json_string = json.dumps(message_dict)

    # 2. Encrypt that string using your function
    # This returns a dict like: {"iv": "...", "data": "..."}
    encrypted_package = encrypt_message(raw_json_string)

    # 3. Convert the encrypted package to a JSON string
    message_to_send = json.dumps(encrypted_package)

    # 4. Send the encrypted string to everyone
    for dst in web_socket_wrappers_array:
        await dst.ws.send_str(message_to_send)

async def send_message_to_player_name(message, player_name: str):
    ws_wrapper = find_ws_from_username(player_name)
    await ws_wrapper.ws.send_str(message)

async def send_message_to_player_wrapper(message: dict, wrapper):

    #convert the dict to a string
    message_as_str = json.dumps(message)

    #Encrypt the string
    encrytped_message = encrypt_message(message_as_str)

    #Turn the encrypted message to a JSON string
    message_to_send = json.dumps(encrytped_message)
    await wrapper.ws.send_str(message_to_send)

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
