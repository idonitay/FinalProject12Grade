// Create a WebSocket connection to your server
const socket = new WebSocket("ws://localhost:8080/ws");

// Fired when the connection is opened
socket.addEventListener("open", () => {
    console.log("Connected to server!");

    let message_as_dict = {
        'opcode':client_2_server['login'], 
        'message': 'hi from Ido'
    };

    // Send a message to the server
    send_message_to_server(message_as_dict);
});

// Fired when a message comes from the server
socket.addEventListener("message", (event) => {
    console.log(event.data);
    let response = JSON.parse(event.data);
    console.log(`opcode: ${response.opcode} message: ${response.message}`);
    switch(response['opcode'])
    {
        case server_2_client['Connection Established']:
            chatbox.displayMassage("server", response["message"], document.getElementById("chat-wrapper"));
            break;

        case server_2_client["Message sent"]:
            console.log(response["message"]);
            chatbox.displayMassage("player", response["message"], document.getElementById("chat-wrapper"));
            break;

        case client_2_server["Message sent"]:
            console.log(response["message"]);
            //chatbox already displays message
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
socket.addEventListener("close", () => {
    console.log("Disconnected from server");
});


function send_message_to_server(json_obj)
{
    console.log(json_obj);
    let message_as_str = JSON.stringify(json_obj);
    socket.send(message_as_str);
}


class encryptor_decryptor
{
    constructor()
    {
        self.keys = crypto.subtle.generateKey(
        { name: "RSA-OAEP",
             modulusLength: 2048,
              publicExponent: new Uint8Array([1,0,1]),
               hash: "SHA-256" },
        true,
        ["encrypt", "decrypt"]
        );

        }
            
    encodeMsg(msg)
    {
        let encrypted = crypto.subtle.encrypt(
            { name: "RSA-OAEP" },
            self.keys.publicKey,
            new TextEncoder().encode(msg)
        );
        return encrypted;
    }

    decodeMsg()
    {
        let decrypted = crypto.subtle.decrypt(
            { name: "RSA-OAEP" },
            self.keys.privateKey,
            encrypted
        );

        console.log(new TextDecoder().decode(decrypted));

        return decrypted;
        // Hi!

    }

}