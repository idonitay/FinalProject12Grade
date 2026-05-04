import base64
import os
from aiohttp import web
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SECRET_KEY = b"12345678901234567890123456789012"

def decrypt_message(iv_b64: str, data_b64: str) -> str:
    """
    Decrypts the AES-GCM encrypted payload on the server.
    """
    iv = base64.b64decode(iv_b64)
    encrypted_data = base64.b64decode(data_b64)

    aesgcm = AESGCM(SECRET_KEY)

    decrypted = aesgcm.decrypt(
        iv,
        encrypted_data,
        None
    )

    return decrypted.decode()


def encrypt_message(key: bytes, message_str: str) -> dict:
    """
    Encrypts a message using AES-GCM and returns a dictionary
    containing the IV and the encrypted data, both in Base64.
    """
    # AES-GCM requires a 12-byte (96-bit) Initialization Vector (IV)
    iv = os.urandom(12)

    # Initialize the AESGCM cipher with your 16, 24, or 32-byte key
    aesgcm = AESGCM(key)

    # Encrypt the message
    encrypted_bytes = aesgcm.encrypt(iv, message_str.encode('utf-8'), None)

    # Convert to base64 strings to send via JSON
    return {
        "iv": base64.b64encode(iv).decode('utf-8'),
        "data": base64.b64encode(encrypted_bytes).decode('utf-8')
    }