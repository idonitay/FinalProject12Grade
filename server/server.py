import asyncio
from aiohttp import web
import json
import opcodes
import random
import hashlib
import hmac
import base64

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


# --- HTTP handlers ---
async def index(request):
    content = open(f"{STATIC_DIR}/Scribble.html", "rt").read()
    return web.Response(text=content, content_type="text/html")


async def handle_user_message(source_wrapper: WebSocketWrapper, user_message: dict) -> dict:
    print(f"Processing message with opcode: {user_message.get('opcode')}")
    opcode = user_message.get('opcode')
    global word

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
        hash2 = hashlib.sha256(word.encode()).digest()

        if hmac.compare_digest(hash1, hash2):
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
                    'id': source_wrapper.id
                }
            return {}
        else:
            return {
                'opcode': opcodes.server_2_client['Message sent'],
                'message': msg_text,
                'src': source_wrapper.username,
                'id': source_wrapper.id
            }

    elif opcode == opcodes.client_2_server['Draw']:
        return {'opcode': opcodes.server_2_client['Draw'], 'message': user_message['message'],
                'src': source_wrapper.username}

    elif opcode == opcodes.client_2_server['Request word']:
        word = random.choice(words)
        return {'opcode': opcodes.server_2_client['You got a word'], 'message': word, 'src': "server"}

    elif opcode == opcodes.server_2_client['Change username']:
        source_wrapper.username = user_message['message']

    # Add other opcodes as needed here...
    return {'opcode': "unknown", 'received_opcode': opcode}


# --- WebSocket handler ---
async def websocket_handler(request):
    global web_socket_wrappers_array
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    wrapper = WebSocketWrapper(ws)
    web_socket_wrappers_array.append(wrapper)
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
                # We check for the public_key field to identify the initial login
                if "public_key" in payload:
                    print(f"Handshake initiated by: {payload.get('src', 'unknown')}")

                    # 1. Generate Server ECDH Keys
                    server_private_key = ec.generate_private_key(ec.SECP256R1())

                    # 2. Decode Client Public Key and Derive Shared Secret
                    client_public_raw = base64.b64decode(payload["public_key"])
                    client_pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), client_public_raw)
                    shared_secret = server_private_key.exchange(ec.ECDH(), client_pub)

                    # 3. Derive 64 bytes of key material (32 for AES, 32 for HMAC)
                    derived_keys = HKDF(
                        algorithm=hashes.SHA256(),
                        length=64,
                        salt=None,
                        info=b'handshake data',
                    ).derive(shared_secret)

                    wrapper.aes_key = derived_keys[:32]
                    wrapper.hmac_key = derived_keys[32:]

                    # 4. Process Login Logic in handle_user_message
                    response = await handle_user_message(wrapper, payload)

                    # 5. Export Server Public Key to send back to client
                    server_pub_bytes = server_private_key.public_key().public_bytes(
                        encoding=serialization.Encoding.X962,
                        format=serialization.PublicFormat.UncompressedPoint
                    )
                    response["server_public_key"] = base64.b64encode(server_pub_bytes).decode('utf-8')

                    # 6. Send Response as PLAIN JSON
                    await ws.send_str(json.dumps(response))
                    continue

                    # --- PHASE 2: SECURE MESSAGING (ENCRYPTED) ---
                else:
                    try:
                        # Safety Check: Ensure handshake happened first
                        if not hasattr(wrapper, 'aes_key'):
                            print("Discarding message: Handshake not yet completed.")
                            continue

                        # 1. Decrypt and Verify the payload
                        decrypted_json = decrypt_and_verify(payload, wrapper.aes_key, wrapper.hmac_key)
                        user_message = json.loads(decrypted_json)

                        # 2. Pass the real message to game logic
                        response_dict = await handle_user_message(wrapper, user_message)

                        # 3. ROUTING: Send the result where it needs to go
                        if response_dict:
                            # If the user sent to "broadcast", or the server logic requires a broadcast
                            if user_message.get('dst') == "broadcast" or response_dict.get('dst') == "broadcast":
                                await broadcast_message(response_dict)
                            else:
                                # Otherwise, send privately to the sender
                                await send_message_to_player_wrapper(response_dict, wrapper)

                    except Exception as e:
                        print(f"Secure processing error: {e}")

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        print("WebSocket disconnected")
        if wrapper in web_socket_wrappers_array:
            web_socket_wrappers_array.remove(wrapper)
    return ws

# --- Helper Functions ---
async def broadcast_message(message_dict: dict):
    raw_json = json.dumps(message_dict)
    for wrapper in web_socket_wrappers_array:
        if hasattr(wrapper, 'aes_key') and wrapper.aes_key:
            encrypted = encrypt_and_sign(raw_json, wrapper.aes_key, wrapper.hmac_key)
            await wrapper.ws.send_str(json.dumps(encrypted))


async def send_message_to_player_wrapper(message: dict, wrapper):
    raw_json = json.dumps(message)
    encrypted = encrypt_and_sign(raw_json, wrapper.aes_key, wrapper.hmac_key)
    await wrapper.ws.send_str(json.dumps(encrypted))


async def send_updated_score_message(i: int, score: int, player_name: str):
    message = {
        'opcode': opcodes.server_2_client['Update score'],
        'score': score, 'index': i, 'player_name': player_name, 'src': "server"
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