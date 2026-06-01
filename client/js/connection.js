// Create a WebSocket connection to your server
const socket = new WebSocket("ws://localhost:8080/ws");

let username = navigator.userAgent.indexOf('Chrome') === -1 ? "safari" : "chrome";
const user_id = Math.floor(Math.random() * 2000000);

// Fired when the connection is opened
socket.addEventListener("open", async () => {
    console.log("Connected to server!");

    // 1. Check if we already have keys (to handle potential reconnects)
    const keys = await getStoredKeys();
    
    // 2. We always generate a NEW keypair for a NEW socket connection
    // because the Python server clears keys when a socket closes.
    const clientKeyPair = await window.crypto.subtle.generateKey(
        { name: "ECDH", namedCurve: "P-256" },
        true, 
        ["deriveBits"]
    );

    // 3. Save the private key to the window so finishHandshake can find it
    window.pendingPrivateKey = clientKeyPair.privateKey;

    // 4. Export the public part to send to the server
    const publicRaw = await window.crypto.subtle.exportKey("raw", clientKeyPair.publicKey);
    const publicBase64 = toBase64(publicRaw);

    // 5. Construct the login message
    let message_as_dict = {
        'opcode': client_2_server['login'], 
        'message': 'Handshake request',
        'src': username,
        'dst': "server",
        "id": user_id,
        "public_key": toBase64(publicRaw), 
    };

    // 6. Send the plain JSON login/handshake message
    // We don't encrypt this because the server doesn't have our keys yet!
    socket.send(JSON.stringify(message_as_dict));
});


// Fired when a message comes from the server
socket.addEventListener("message", async (event) => {
    let response;
    let rawData = JSON.parse(event.data);

    // 1. Check if this is the "Login Success/Handshake" response
    // These arrive as plain JSON because keys aren't finished yet
    if (rawData.opcode === server_2_client['Connection Established'] || rawData.server_public_key) 
    {
        if (rawData.server_public_key) 
        {
            await finishHandshake(rawData.server_public_key);
            await send_server_ready_message();
        }

        console.log("Handshake Success:", rawData.message);
        return; // <--- CRITICAL: Stop here so we don't hit the switch below!
    } 

    // 2. Secure Phase
    try {
        const { aesKey, hmacKey } = await getStoredKeys();
        if (!aesKey || !hmacKey) throw new Error("No keys found");
        
        const decryptedText = await verifyAndDecryptMessage(rawData, aesKey, hmacKey);
        response = JSON.parse(decryptedText);
    } 
    catch (error) 
    {
        console.error("Security Error:", error.message);
        return;
    }

    switch(response['opcode']) 
    {
        
        case server_2_client["Message sent"]:
            console.log(response["message"]);
            console.log(response["src"])
            chatbox.displayMessage(response["src"], response["message"], document.getElementById("chat-history"), response['id']);
            break;

        case server_2_client["Pong"]:
            break;

        case server_2_client["Draw"]:
            let stroke_dict = response["message"]    

            drawLine(canvas, stroke_dict["pointA"],
                 stroke_dict["pointB"], true, stroke_dict["color"],
                  stroke_dict["size"])

            break;
        
        case server_2_client["Delete canvas"]:
            clearCanvas();

            break;

        case server_2_client["You got a word"]:
            display_current_word(response["message"]);
            console.log("word: " + response["message"])
            canDraw = true;
            break;

        case server_2_client["There is a new current player"]:
            display_current_word("");
            //chatbox.displayMessage(response["src"], response["message"], document.getElementById("chat-history"));     
            chatbox.displayMessage(response["src"], response["message"], document.getElementById("chat-history"));
            canDraw = false;
            break;

        case server_2_client["A word was guessed"]:
            chatbox.displayMessage(response["src"], response["message"], document.getElementById("chat-history"));     
            break;

        case server_2_client["Start timer"]:
            seconds_amount = response['duration'];
            duration = seconds_amount * 1000;
            if (currentTimer != null)
            {
                stop_timer();
            }
            await start_timer(duration);
            clearCanvas();
            break;

        case server_2_client["Reveal word"]:
            chatbox.displayMessage(response["src"], response["message"], document.getElementById("chat-history")); 
            break;

        case server_2_client["Update score"]:
            score_board.updateScoreLineByIndex(response["index"], response["score"], response["player_name"]);
            break;

        case server_2_client["Game ended"]:
            chatbox.displayMessage(response["src"], response["message"], document.getElementById("chat-history")); 
            stop_timer();
            break;

        case server_2_client["First player"]:
            create_start_game_button(document.getElementById("start_game_button_wrapper"));
            break;

        default:
            console.error("Unindentified message:", response['opcode']);
    }
});

// Fired if an error happens
socket.addEventListener("error", (error) => {
    console.error("WebSocket error:", error);
});

// Fired when the connection closes
socket.addEventListener("close", (event) => {
    console.log("Disconnected from server");
});

async function PingPong() {
  
    let message_as_dict = {
        'opcode': client_2_server['Ping'], 
        'message': 'ping',
        'dst': "server"
    };

    // Send a message to the server
    await send_message_to_server(message_as_dict);
}

// Helper function to keep the listener clean
async function finishHandshake(serverPublicBase64) {
    try {
        if (!window.pendingPrivateKey) {
            throw new Error("Private key missing. Handshake cannot proceed.");
        }

        const serverPublicRaw = fromBase64(serverPublicBase64);

        // 1. Import the Server's Public Key
        const serverPublicKey = await window.crypto.subtle.importKey(
            "raw",
            serverPublicRaw,
            { name: "ECDH", namedCurve: "P-256" },
            true,
            []
        );

        // 2. Derive the base Shared Secret (256 bits)
        const sharedSecret = await window.crypto.subtle.deriveBits(
            { name: "ECDH", public: serverPublicKey },
            window.pendingPrivateKey,
            256
        );

        // 3. Use HKDF to expand the secret (Matching Python's HKDF)
        const extractKey = await window.crypto.subtle.importKey(
            "raw", 
            sharedSecret, 
            "HKDF", 
            false, 
            ["deriveBits"]
        );

        const derivedBits = await window.crypto.subtle.deriveBits(
            {
                name: "HKDF",
                hash: "SHA-256",
                salt: new Uint8Array(), // Matching Python's salt=None
                info: new TextEncoder().encode("handshake data") // Matching Python's info
            },
            extractKey,
            512 // We need 64 bytes total (32 for AES, 32 for HMAC)
        );

        // 4. Import the specific keys
        const aesKey = await window.crypto.subtle.importKey(
            "raw",
            derivedBits.slice(0, 32),
            { name: "AES-GCM" },
            false,
            ["encrypt", "decrypt"]
        );

        const hmacKey = await window.crypto.subtle.importKey(
            "raw",
            derivedBits.slice(32, 64),
            { name: "HMAC", hash: "SHA-256" },
            false,
            ["sign", "verify"]
        );

        // 5. SAVE THE KEYS (The missing step)
        await saveKeys(aesKey, hmacKey);

        // Cleanup
        delete window.pendingPrivateKey;
        console.log("Secure session established and keys saved!");

    } 
    catch (e) 
    {
        console.error("Handshake Error:", e.message);
    }
}


async function DeclareCurrentPlayer()
{
    let message_as_dict = {
        'opcode': client_2_server['I am current player'], 
        'message': '',
        'dst': "broadcast"
    };

    // Send a message to the server
    await send_message_to_server(message_as_dict);
}

async function send_server_ready_message() 
{
      let message_as_dict = {
        'opcode': client_2_server['Ready'], 
        'message': '',
        'dst': "server"
    };

    // Send a message to the server
    await send_message_to_server(message_as_dict);  
}

async function requestWordFromServer() 
{
    console.log("request word")
    let message_as_dict = {
        'opcode': client_2_server['Request word'], 
        'message': '',
        'dst': "server"
    };

    // Send a message to the server
    await send_message_to_server(message_as_dict);
}

function display_current_word(word)
{
    document.getElementById("word-div").innerHTML = word;
}

function display_timer(time)
{
    document.getElementById("timer-div").innerHTML = time;
}

async function send_timer_ended_message()
{
    let message_as_dict = {
        'opcode': client_2_server['Timer ended'], 
        'message': '',
        'dst': "broadcast"
    };

    // Send a message to the server
    await send_message_to_server(message_as_dict);
}

async function send_drawing_to_players()
{
    let message_as_dict = {
        'opcode': client_2_server['Draw'], 
        'message': turn_canvas_to_dict(canvas),
        'dst': "broadcast"
    };

    await send_message_to_server(message_as_dict);

}

async function clear_everybody_canvas()
{
    let message_as_dict = {
        'opcode': client_2_server['Delete canvas'], 
        'message': '',
        'dst': "broadcast"
    };

    await send_message_to_server(message_as_dict);
}

// Call the function every 1000 milliseconds (1 second)

async function send_message_to_server(message_as_dict) 
{
    // 1. If this is the LOGIN message, send it as plain JSON (no keys exist yet!)
    if (message_as_dict.opcode === client_2_server['login']) {
        socket.send(JSON.stringify(message_as_dict));
        return;
    }

    // 2. For ALL other messages, get the keys from the vault
    const { aesKey, hmacKey } = await getStoredKeys();

    if (!aesKey || !hmacKey) {
        console.error("No secure session found. Please login first.");
        return;
    }

    // 3. Encrypt and Sign the message
    // We stringify the dict first so we can encrypt the whole thing
    const securePacket = await encryptAndSignMessage(
        JSON.stringify(message_as_dict), 
        aesKey, 
        hmacKey
    );

    // 4. Send the secure packet (iv, data, signature)
    
    socket.send(JSON.stringify(securePacket));
}

// class encryptor_decryptor
// {
//     constructor()
//     {
//         self.keys = crypto.subtle.generateKey(
//         { name: "RSA-OAEP",
//              modulusLength: 2048,
//               publicExponent: new Uint8Array([1,0,1]),
//                hash: "SHA-256" },
//         true,
//         ["encrypt", "decrypt"]
//         );

//         }
            
//     encodeMsg(msg)
//     {
//         let encrypted = crypto.subtle.encrypt(
//             { name: "RSA-OAEP" },
//             self.keys.publicKey,
//             new TextEncoder().encode(msg)
//         );
//         return encrypted;
//     }

//     decodeMsg()
//     {
//         let decrypted = crypto.subtle.decrypt(
//             { name: "RSA-OAEP" },
//             self.keys.privateKey,
//             encrypted
//         );

//         console.log(new TextDecoder().decode(decrypted));

//         return decrypted;
//         // Hi!

//     }

// }