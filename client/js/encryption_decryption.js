// --- 1. KEY VAULT (IndexedDB) ---
async function openKeyDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("KeyVault", 1);
        request.onupgradeneeded = () => {
            request.result.createObjectStore("secure_keys");
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// --- 1. LOCAL MEMORY KEY VAULT (Isolates separate browser tabs) ---
async function saveKeys(aesKey, hmacKey) {
    // Save keys directly to the current tab's execution window context 
    // instead of writing to a shared global IndexedDB database instance!
    window.activeSessionAesKey = aesKey;
    window.activeSessionHmacKey = hmacKey;
    return Promise.resolve();
}

async function getStoredKeys() {
    // Fetch clean isolated references that cannot be overwritten by other tabs
    return { 
        aesKey: window.activeSessionAesKey, 
        hmacKey: window.activeSessionHmacKey 
    };
}

// --- 2. HELPERS ---
function toBase64(buffer) {
    return btoa(String.fromCharCode(...new Uint8Array(buffer)));
}

function fromBase64(base64String) {
    const binaryString = window.atob(base64String);
    return Uint8Array.from(binaryString, (char) => char.charCodeAt(0));
}

// --- 3. AUTHENTICATED ENCRYPTION (Encrypt-then-MAC) ---
async function encryptAndSignMessage(text, aesKey, hmacKey) {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encodedText = new TextEncoder().encode(text);

    const encryptedBuffer = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        aesKey,
        encodedText
    );

    // Create signature over IV + Ciphertext
    const combinedData = new Uint8Array(iv.length + encryptedBuffer.byteLength);
    combinedData.set(iv);
    combinedData.set(new Uint8Array(encryptedBuffer), iv.length);

    const signatureBuffer = await crypto.subtle.sign("HMAC", hmacKey, combinedData);

    return {
        iv: toBase64(iv),
        data: toBase64(encryptedBuffer),
        signature: toBase64(signatureBuffer)
    };
}

async function verifyAndDecryptMessage(encryptedObject, aesKey, hmacKey) {
    const iv = fromBase64(encryptedObject.iv);
    const data = fromBase64(encryptedObject.data);
    const signature = fromBase64(encryptedObject.signature);

    const combinedData = new Uint8Array(iv.length + data.length);
    combinedData.set(iv);
    combinedData.set(data, iv.length);

    const isValid = await crypto.subtle.verify("HMAC", hmacKey, signature, combinedData);
    if (!isValid) throw new Error("Security check failed: Message tampered.");

    const decrypted = await crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, aesKey, data);
    return new TextDecoder().decode(decrypted);
}