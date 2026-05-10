// Create a WebSocket connection to your server
const socket = new WebSocket("ws://localhost:8080/ws");

let username = navigator.userAgent.indexOf('Chrome') === -1 ? "safari" : "chrome";
const user_id = Math.floor(Math.random() * 2000000);

// Fired when the connection is opened
socket.addEventListener("open", async () => {
    console.log("Connected to server!");

    // 1. Generate local DH keys for this session
    const clientKeyPair = await window.crypto.subtle.generateKey(
        { name: "ECDH", namedCurve: "P-256" },
        true, 
        ["deriveBits"]
    );

    // 2. Export the public part to send to the server
    const publicRaw = await window.crypto.subtle.exportKey("raw", clientKeyPair.publicKey);
    const publicBase64 = toBase64(publicRaw);

    // 3. Add the key to your existing login message
    let message_as_dict = {
        'opcode': client_2_server['login'], 
        'message': 'hi from Ido',
        'src': username,
        'dst': "server",
        "id": user_id,
        "public_key": publicBase64 // <-- Your "Paint Mix" goes here
    };

    // 4. Temporarily store the private key so we can use it when the server responds
    window.pendingPrivateKey = clientKeyPair.privateKey;

    await send_message_to_server(message_as_dict);
});


// Fired when a message comes from the server
socket.addEventListener("message", async (event) => {
    let response;
    let rawData = JSON.parse(event.data);

    // 1. Check if this is the "Login Success/Handshake" response
    // These arrive as plain JSON because keys aren't finished yet
    if (rawData.opcode === server_2_client['Connection Established'] || rawData.server_public_key) {
        response = rawData;

        // If the server sent a public key, finish the Handshake
        if (rawData.server_public_key) {
            await finishHandshake(rawData.server_public_key);
        }
    } 
    else {
        // 2. For all other messages, Decrypt and Verify
        try {
            const { aesKey, hmacKey } = await getStoredKeys();
            
            // This calls your new verifyAndDecryptMessage function
            const decryptedText = await verifyAndDecryptMessage(rawData, aesKey, hmacKey);
            response = JSON.parse(decryptedText);
        } catch (error) {
            console.error("Security Error:", error.message);
            return; // Drop the message if it's tampered or keys are missing
        }
    }
    
    switch(response['opcode']) 
    {

        case server_2_client["Message sent"]:
            console.log(response["message"]);
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
async function finishHandshake(serverPublicBase64) 
{
    const serverPublicRaw = fromBase64(serverPublicBase64);
    const serverPublicKey = await window.crypto.subtle.importKey(
        "raw", serverPublicRaw, { name: "ECDH", namedCurve: "P-256" }, true, []
    );

    const sharedBits = await window.crypto.subtle.deriveBits(
        { name: "ECDH", public: serverPublicKey },
        window.pendingPrivateKey, 
        512 
    );

    const aesKey = await crypto.subtle.importKey(
        "raw", sharedBits.slice(0, 32), "AES-GCM", false, ["encrypt", "decrypt"]
    );
    const hmacKey = await crypto.subtle.importKey(
        "raw", sharedBits.slice(32, 64), "HMAC", false, ["sign", "verify"]
    );

    await saveKeys(aesKey, hmacKey);
    delete window.pendingPrivateKey;
    console.log("Secure session keys saved to IndexedDB.");
}

async function requestWordFromServer()
{
    let message_as_dict = {
        'opcode': client_2_server['Request word'], 
        'message': '',
        'dst': "server"
    };

    // Send a message to the server
    await send_message_to_server(message_as_dict);

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