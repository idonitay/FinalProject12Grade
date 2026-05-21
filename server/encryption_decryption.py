import base64
import os
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decrypt_and_verify(payload: dict, aes_key: bytes, hmac_key: bytes) -> str:
    """
    Verifies the HMAC-SHA256 signature and decrypts the authenticated
    AES-GCM payload matching WebCrypto specification exactly.
    """
    try:
        # Explicitly extract and decode Base64 data strings to pure byte segments
        iv = base64.b64decode(payload["iv"])
        ciphertext = base64.b64decode(payload["data"])
        signature = base64.b64decode(payload["signature"])
    except KeyError as e:
        raise KeyError(f"Secure envelope missing key structural field: {e}")
    except Exception:
        raise ValueError("Cryptographic parameters are not properly Base64 encoded.")

    # 1. Reconstruct Signature Data Context (IV + Ciphertext concatenated natively)
    # This mirrors 'combinedData' Uint8Array composition in WebCrypto API
    authenticated_data = iv + ciphertext

    # 2. Verify Message Integrity using a constant-time comparison
    h = hmac.new(hmac_key, authenticated_data, hashlib.sha256)
    if not hmac.compare_digest(h.digest(), signature):
        raise PermissionError("Security validation failed: MAC authentication tag signature mismatch.")

    # 3. Decrypt Content
    aesgcm = AESGCM(aes_key)
    # WebCrypto uses no associated authenticated data (None) inside standard AES-GCM envelopes
    decrypted_bytes = aesgcm.decrypt(iv, ciphertext, None)

    return decrypted_bytes.decode('utf-8')


def encrypt_and_sign(message_str: str, aes_key: bytes, hmac_key: bytes) -> dict:
    """
    Encrypts an outgoing plain text string using AES-GCM and appends
    a verifiable HMAC signature for secure delivery to the client layer.
    """
    # Generate an explicit 12-byte initialization vector (Standard for AES-GCM)
    iv = os.urandom(12)

    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(iv, message_str.encode('utf-8'), None)

    # Calculate HMAC over binary sequence
    authenticated_data = iv + ciphertext
    h = hmac.new(hmac_key, authenticated_data, hashlib.sha256)

    # Package objects as Base64 strings to ensure transport-layer compatibility over WebSockets
    return {
        "iv": base64.b64encode(iv).decode('utf-8'),
        "data": base64.b64encode(ciphertext).decode('utf-8'),
        "signature": base64.b64encode(h.digest()).decode('utf-8')
    }