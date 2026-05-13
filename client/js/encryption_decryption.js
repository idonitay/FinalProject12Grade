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

async function saveKeys(aesKey, hmacKey) {
    const db = await openKeyDB();
    const tx = db.transaction("secure_keys", "readwrite");
    const store = tx.objectStore("secure_keys");
    store.put(aesKey, "active_aes");
    store.put(hmacKey, "active_hmac");
    return new Promise((resolve) => tx.oncomplete = resolve);
}

async function getStoredKeys() {
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