import asyncio
from aiohttp import web
import json
import opcodes
import random
import hashlib
import hmac
import base64
import copy

from web_socket_wrapper import WebSocketWrapper
from encryption_decryption import decrypt_and_verify
from encryption_decryption import encrypt_and_sign
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from db_conn import get_words_from_db

STATIC_DIR = "../client"
web_socket_wrappers_array = []
words = get_words_from_db()
word = ""
duration_in_seconds = 60
amount_of_rounds = 3
amount_of_turns = len(web_socket_wrappers_array) * amount_of_rounds
current_turn_index = 0

# --- HTTP handlers ---
async def index(request):
    content = open(f"{STATIC_DIR}/Scribble.html", "rt").read()
    return web.Response(text=content, content_type="text/html")


async def handle_user_message(source_wrapper: WebSocketWrapper, user_message: dict) -> dict:
    print(f"Processing message with opcode: {user_message.get('opcode')}")
    opcode = user_message.get('opcode')
    global word
    global current_turn_index

    if opcode == opcodes.client_2_server['login']:
        source_wrapper.username = user_message.get('src', 'Unknown')
        source_wrapper.id = user_message.get('id')
        return {
            'opcode': opcodes.server_2_client["Connection Established"],
            'message': "connection established",
            'src': source_wrapper.username
        }

    elif opcode == opcodes.client_2_server['Message sent']:
        msg_text = user_message.get("message", "")
        hash1 = hashlib.sha256(msg_text.encode()).digest()
        hash2 = hashlib.sha256(word.encode()).digest() if word else b""

        if word and hmac.compare_digest(hash1, hash2):
            if not source_wrapper.answered:
                source_wrapper.score += 100
                idx = find_index_based_on_ws(source_wrapper)

                await send_updated_score_message(idx, source_wrapper.score, source_wrapper.username)

                source_wrapper.answered = True
                if not source_wrapper.current_player:
                    return {
                        'opcode': opcodes.server_2_client["A word was guessed"],
                        'message': f"{source_wrapper.username} has guessed the word correctly",
                        'src': "server",
                        'id': source_wrapper.id,
                        'dst': 'broadcast'
                    }

            return {
                'opcode': opcodes.server_2_client["Message sent"],
                'message': f"{source_wrapper.username} has already guessed the word correctly",
                'src': source_wrapper.username,
                'id': source_wrapper.id,
                'dst': 'broadcast'
            }

        else:
            return {
                'opcode': opcodes.server_2_client['Message sent'],
                'message': msg_text,
                'src': source_wrapper.username,
                'id': source_wrapper.id,
                'dst': 'broadcast'
            }

    elif opcode == opcodes.client_2_server['Draw']:
        return {
            'opcode': opcodes.server_2_client['Draw'],
            'message': user_message['message'],
            'src': source_wrapper.username,
            'dst': 'broadcast'
        }

    elif opcode == opcodes.client_2_server['Request word']:
        word = random.choice(words)
        return {
            'opcode': opcodes.server_2_client['You got a word'],
            'message': word,
            'src': "server"
        }

    elif opcode == opcodes.client_2_server['Change username']:
        source_wrapper.username = user_message['message']
        return {}

    elif opcode == opcodes.client_2_server['I am current player']:
        await send_start_timer_message()
        current_turn_index += 1
        source_wrapper.answered = True
        return {
            'opcode': opcodes.server_2_client['There is a new current player'],
            'src': "server",
            'message': f"{source_wrapper.username} is the current player",
        }

    elif opcode == opcodes.client_2_server['Timer ended']:
        await finish_turn()
        return {}

    return {
        'opcode': "unknown",
        'received_opcode': opcode
    }


# --- WebSocket handler ---
async def websocket_handler(request):
    global web_socket_wrappers_array
    global amount_of_turns

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    wrapper = WebSocketWrapper(ws)
    wrapper.ws = ws
    web_socket_wrappers_array.append(wrapper)
    amount_of_turns = amount_of_rounds * len(web_socket_wrappers_array)
    print(f"WebSocket connected. Total clients: {len(web_socket_wrappers_array)}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    payload = json.loads(msg.data)
                except json.JSONDecodeError:
                    print("Received malformed JSON")
                    continue

                # --- PHASE 1: THE HANDSHAKE (PLAIN TEXT) ---
                if "public_key" in payload:
                    print(f"Handshake initiated by: {payload.get('src', 'unknown')}")

                    server_private_key = ec.generate_private_key(ec.SECP256R1())

                    client_public_raw = base64.b64decode(payload["public_key"])
                    client_pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), client_public_raw)
                    shared_secret = server_private_key.exchange(ec.ECDH(), client_pub)

                    derived_keys = HKDF(
                        algorithm=hashes.SHA256(),
                        length=64,
                        salt=None,
                        info=b'handshake data',
                    ).derive(shared_secret)

                    wrapper.aes_key = derived_keys[:32]
                    wrapper.hmac_key = derived_keys[32:]

                    response = await handle_user_message(wrapper, payload)

                    server_pub_bytes = server_private_key.public_key().public_bytes(
                        encoding=serialization.Encoding.X962,
                        format=serialization.PublicFormat.UncompressedPoint
                    )
                    response["server_public_key"] = base64.b64encode(server_pub_bytes).decode('utf-8')

                    await ws.send_str(json.dumps(response))
                    continue

                # --- PHASE 2: SECURE MESSAGING (ENCRYPTED) ---
                else:
                    try:
                        if not hasattr(wrapper, 'aes_key'):
                            print("Discarding message: Handshake not yet completed.")
                            continue

                        decrypted_json = decrypt_and_verify(payload, wrapper.aes_key, wrapper.hmac_key)
                        user_message = json.loads(decrypted_json)

                        response_dict = await handle_user_message(wrapper, user_message)

                        if response_dict:
                            if user_message.get('dst') == "broadcast" or response_dict.get('dst') == "broadcast":
                                response_dict['dst'] = 'broadcast'
                                await broadcast_message(response_dict)
                            else:
                                await send_message_to_player_wrapper(response_dict, wrapper)

                        if check_if_everyone_answered():
                            await finish_turn()


                    except Exception as msg_error:
                        print(f"Error handling secure messaging packet: {msg_error}")
                        continue

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        print("WebSocket disconnected")
        if wrapper in web_socket_wrappers_array:
            web_socket_wrappers_array.remove(wrapper)
            amount_of_turns = amount_of_rounds * len(web_socket_wrappers_array)
    return ws


# --- Helper Functions ---
async def broadcast_message(message_dict: dict):
    for wrapper in list(web_socket_wrappers_array):
        try:
            if hasattr(wrapper, 'aes_key') and wrapper.aes_key and hasattr(wrapper, 'ws') and wrapper.ws:
                # Isolate the original dictionary before encryption string transformation
                local_message_copy = copy.deepcopy(message_dict)
                raw_json = json.dumps(local_message_copy)

                encrypted = encrypt_and_sign(raw_json, wrapper.aes_key, wrapper.hmac_key)
                await wrapper.ws.send_str(json.dumps(encrypted))
        except Exception as e:
            print(f"Skipping client broadcast wrapper due to collision: {e}")
            continue


async def choose_next_player():
    global web_socket_wrappers_array
    global word
    global words

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


async def send_message_to_player_wrapper(message: dict, wrapper):
    try:
        if hasattr(wrapper, 'aes_key') and wrapper.aes_key and hasattr(wrapper, 'ws') and wrapper.ws:
            local_copy = copy.deepcopy(message)
            raw_json = json.dumps(local_copy)
            encrypted = encrypt_and_sign(raw_json, wrapper.aes_key, wrapper.hmac_key)
            await wrapper.ws.send_str(json.dumps(encrypted))
    except Exception as e:
        print(f"Direct transmission delivery crash: {e}")

async def finish_turn():
    global current_turn_index



    reset_answered()
    await reveal_word()
    await choose_next_player()
    await send_start_timer_message()

    current_turn_index += 1
    if current_turn_index > amount_of_turns:
        await send_endgame_message()
        return

async def send_endgame_message():

    winners = find_winners()
    winners_username = winners[0].username
    for i in range(1, len(winners)):
        winners_username = winners_username + ", " + winners[i].username

    message = {
        'opcode': opcodes.server_2_client['Game ended'],
        'message': f"{winners_username} has won!",
        'src': "server",
    }

    await broadcast_message(message)

def find_winners():
    global web_socket_wrappers_array
    max_score = -1
    current_winners = []
    for wrapper in web_socket_wrappers_array:
        if wrapper.score > max_score:
            max_score = wrapper.score
            current_winners = [wrapper]

        elif wrapper.score == max_score:
            current_winners.append(wrapper)

    return current_winners


async def reveal_word():
    global word

    message = {
        'opcode': opcodes.server_2_client['Reveal word'],
        'message': f"The word was {word}",
        'src': "server",
    }

    await broadcast_message(message)

async def send_start_timer_message():
    global duration_in_seconds

    message = {
        'opcode': opcodes.server_2_client['Start timer'],
        'duration': duration_in_seconds,
        'src': "server",
    }

    await broadcast_message(message)

async def send_updated_score_message(i: int, score: int, player_name: str):
    message = {
        'opcode': opcodes.server_2_client['Update score'],
        'score': score,
        'index': i,
        'player_name': player_name,
        'src': "server",
    }
    await broadcast_message(message)


def find_index_based_on_ws(target_wrapper) -> int:
    for i, wrapper in enumerate(web_socket_wrappers_array):
        if wrapper == target_wrapper:
            return i
    return -1


def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/", path=STATIC_DIR)
    web.run_app(app, host="localhost", port=8080)


if __name__ == "__main__":
    main()