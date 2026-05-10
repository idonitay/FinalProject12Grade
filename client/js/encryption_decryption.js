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


// --- 1. KEY VAULT (IndexedDB) ---
// This stores the keys so they survive a page refresh

async function openKeyDB() 
{
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("KeyVault", 1);
        request.onupgradeneeded = () => {
            request.result.createObjectStore("secure_keys");
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function saveKeys(aesKey, hmacKey) 
{
    const db = await openKeyDB();
    const tx = db.transaction("secure_keys", "readwrite");
    const store = tx.objectStore("secure_keys");
    store.put(aesKey, "active_aes");
    store.put(hmacKey, "active_hmac");
    return new Promise((resolve) => tx.oncomplete = resolve);
}

async function getStoredKeys() 
{
    const db = await openKeyDB();
    const tx = db.transaction("secure_keys", "readonly");
    const store = tx.objectStore("secure_keys");
    const aesReq = store.get("active_aes");
    const hmacReq = store.get("active_hmac");
    return new Promise((resolve) => {
        tx.oncomplete = () => resolve({ aesKey: aesReq.result, hmacKey: hmacReq.result });
    });
}

// --- 2. HELPERS ---

function toBase64(buffer) 
{
    return btoa(String.fromCharCode(...new Uint8Array(buffer)));
}

function fromBase64(base64String) 
{
    const binaryString = window.atob(base64String);
    return Uint8Array.from(binaryString, (char) => char.charCodeAt(0));
}

// --- 3. ENCRYPTION & SIGNING ---

async function encryptAndSignMessage(text, aesKey, hmacKey) 
{
    // 1. Setup IV and Data
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encodedText = new TextEncoder().encode(text);

    // 2. Encrypt (AES-GCM)
    const encryptedBuffer = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        aesKey,
        encodedText
    );

    // 3. Sign (HMAC)
    // We sign the IV + the encrypted data to prevent tampering
    const combinedData = new Uint8Array(iv.length + encryptedBuffer.byteLength);
    combinedData.set(iv);
    combinedData.set(new Uint8Array(encryptedBuffer), iv.length);

    const signatureBuffer = await crypto.subtle.sign(
        "HMAC",
        hmacKey,
        combinedData
    );

    // 4. Return the package
    return {
        iv: toBase64(iv),
        data: toBase64(encryptedBuffer),
        signature: toBase64(signatureBuffer)
    };
}

async function verifyAndDecryptMessage(encryptedObject, aesKey, hmacKey) 
{
    const iv = fromBase64(encryptedObject.iv);
    const data = fromBase64(encryptedObject.data);
    const signature = fromBase64(encryptedObject.signature);

    // 1. Verify Signature first
    const combinedData = new Uint8Array(iv.length + data.length);
    combinedData.set(iv);
    combinedData.set(data, iv.length);

    const isValid = await crypto.subtle.verify(
        "HMAC",
        hmacKey,
        signature,
        combinedData
    );

    if (!isValid) throw new Error("Signature verification failed! Message tampered.");

    // 2. Decrypt
    const decrypted = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: iv },
        aesKey,
        data
    );

    return new TextDecoder().decode(decrypted);
}