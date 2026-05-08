const SECRET_KEY = "12345678901234567890123456789012";

async function getKey() {
    const encoder = new TextEncoder();
    const keyData = encoder.encode(SECRET_KEY);

    // Validate key length for AES-GCM (128 or 256 bits)
    if (keyData.byteLength !== 16 && keyData.byteLength !== 32) {
        throw new Error(`Invalid key length (${keyData.byteLength} bytes). The key must be exactly 16 or 32 bytes long.`);
    }

    try {
        const key = await crypto.subtle.importKey(
            "raw",
            keyData,
            { name: "AES-GCM" },
            false,
            ["encrypt", "decrypt"]
        );
        return key;
    } 
    catch (error) {
        throw error;
    }
}

function toBase64(buffer) {
    return btoa(
        String.fromCharCode(...new Uint8Array(buffer))
    );
}

async function encryptMessage(text) {
    // 1. Convert the secret key string to a CryptoKey
    const key = await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(SECRET_KEY),
        { name: "AES-GCM" },
        false,
        ["encrypt"]
    );

    // 2. Generate a random 12-byte IV (nonce)
    const iv = crypto.getRandomValues(new Uint8Array(12));

    // 3. Encrypt the plaintext string
    const encodedText = new TextEncoder().encode(text);
    const encryptedBuffer = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        encodedText
    );

    // 4. Helper function to convert an ArrayBuffer to Base64
    const bufferToBase64 = (buffer) => {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    };

    return {
        iv: bufferToBase64(iv),
        data: bufferToBase64(encryptedBuffer) // The buffer contains ciphertext + 16-byte tag
    };
}

function fromBase64(base64String) {
    const binaryString = window.atob(base64String);
    return Uint8Array.from(binaryString, (char) => char.charCodeAt(0));
}

async function decryptMessage(encryptedObject) {
    const key = await getKey();

    const decrypted = await crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: fromBase64(encryptedObject.iv) // Now returns a proper Uint8Array
        },
        key,
        fromBase64(encryptedObject.data) // Now returns a proper Uint8Array
    );

    return new TextDecoder().decode(decrypted);
}