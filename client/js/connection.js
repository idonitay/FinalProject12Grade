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
    console.log(response)
    console.log(`opcode: ${response.opcode} message: ${response.message}`);
    switch(response['opcode'])
    {
        case server_2_client['Connection Established']:
            console.log(response["message"]);
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
