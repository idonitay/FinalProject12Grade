// Create a WebSocket connection to your server
const socket = new WebSocket("ws://localhost:8080/ws");

const username = navigator.userAgent.indexOf('Chrome') === -1 ? "safari" : "chrome";
const user_id = Math.floor(Math.random() * 2000000);

// Fired when the connection is opened
socket.addEventListener("open", async () => {
    console.log("Connected to server!");

    let message_as_dict = {
        'opcode': client_2_server['login'], 
        'message': 'hi from Ido',
        'src': username,
        'dst': "server",
        "id": user_id
    };

    // Send a message to the server
    await send_message_to_server(message_as_dict);
});


// Fired when a message comes from the server
socket.addEventListener("message", async (event) => {
    //console.log(event.data);
    // let encryptedObject = JSON.parse(event.data);
    // let decryptedText = await decryptMessage(encryptedObject);
    // let response = JSON.parse(decryptedText);
    let response = JSON.parse(event.data)
    
    console.log(`opcode: ${response.opcode}, message: ${response.message}`);
    switch(response['opcode'])
    {
        case server_2_client['Connection Established']:
            chatbox.displayMessage(response["src"], response["message"], document.getElementById("chat-history"));
            break;

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

async function send_message_to_server(json_obj) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open.");
        return;
    }

    try {
        // Encrypt the stringified JSON object
        let encryptedPayload = await encryptMessage(JSON.stringify(json_obj));
        
        // Send the payload
        socket.send(JSON.stringify(encryptedPayload));
        console.log("Encrypted message sent successfully.");
    } catch (error) {
        console.error("Failed to encrypt or send message:", error);
    }
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