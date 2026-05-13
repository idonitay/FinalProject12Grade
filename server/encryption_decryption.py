import base64
import os
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decrypt_and_verify(payload: dict, aes_key: bytes, hmac_key: bytes) -> str:
    """Verifies HMAC signature and decrypts the AES-GCM payload."""
    iv = base64.b64decode(payload["iv"])
    ciphertext = base64.b64decode(payload["data"])
    signature = base64.b64decode(payload["signature"])

    # 1. Verify Signature (HMAC) - matches client's combinedData logic
    # Ensure bytes are concatenated directly
    h = hmac.new(hmac_key, iv + ciphertext, hashlib.sha256)
    if not hmac.compare_digest(h.digest(), signature):
        raise PermissionError("Security check failed: Message tampered.")

    # 2. Decrypt (AES-GCM)
    aesgcm = AESGCM(aes_key)
    decrypted = aesgcm.decrypt(iv, ciphertext, None)
    return decrypted.decode('utf-8')


def encrypt_and_sign(message_str: str, aes_key: bytes, hmac_key: bytes) -> dict:
    """Encrypts message and adds an HMAC signature."""
    iv = os.urandom(12)
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(iv, message_str.encode('utf-8'), None)

    # Sign IV + Ciphertext
    # Ensure bytes are concatenated directly
    h = hmac.new(hmac_key, iv + ciphertext, hashlib.sha256)

    return {
        "iv": base64.b64encode(iv).decode('utf-8'),
        "data": base64.b64encode(ciphertext).decode('utf-8'),
        "signature": base64.b64encode(h.digest()).decode('utf-8')
    }